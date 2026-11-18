# Code patterns

This is the canonical Kotlin for each concern. When new code follows these shapes, every feature reads the same and a reviewer can compare a PR against this one page. The project's own rules override it. Imports are omitted. The example feature is a notes list.

## Kotlin style
- **Immutability:** `val` over `var`; read-only collection types (`List`, not `MutableList`) in public APIs.
- **Null safety:** no `!!`. Use `?.`, `?:` or `requireNotNull(x) { "reason" }`, or redesign so the value can't be null.
- **Types:**
  - `data class` for models;
  - `sealed interface` for states, actions, events and errors;
  - a `when` over a sealed type lists every subtype, with no `else`.
- **Functions:** one job each, under ~30 lines. Use expression bodies when they fit on one line.
- **Names say what, not how:** `observeNotes()`, `RefreshNotesUseCase`, `NotesUiState`. Booleans read as questions: `isLoading`, `hasMore`.
- **Named arguments** for booleans and for parameters of the same type: `Note(id = id, title = title, …)`.
- **No magic values:** `private const val` for constants; resources for anything the user sees.
- **Visibility:** `internal` by default in modules, `private` within files.
- **Comments** explain *why*, never *what*. KDoc only on public APIs that aren't obvious.

## Domain (pure Kotlin)
```kotlin
data class Note(val id: String, val title: String, val body: String, val updatedAt: Instant)

sealed interface AppError {
    data object Network : AppError
    data object Unauthorized : AppError
    data object NotFound : AppError
    data class Server(val code: Int) : AppError
    data class Unknown(val cause: Throwable) : AppError
}

sealed interface AppResult<out T> {
    data class Success<out T>(val data: T) : AppResult<T>
    data class Failure(val error: AppError) : AppResult<Nothing>
}

interface NoteRepository {
    fun observeNotes(): Flow<List<Note>>
    suspend fun refresh(): AppResult<Unit>
}

class ObserveNotesUseCase @Inject constructor(private val noteRepository: NoteRepository) {
    operator fun invoke(): Flow<List<Note>> =
        noteRepository.observeNotes().map { notes -> notes.sortedByDescending(Note::updatedAt) }
}

class RefreshNotesUseCase @Inject constructor(private val noteRepository: NoteRepository) {
    suspend operator fun invoke(): AppResult<Unit> = noteRepository.refresh()
}
```
- One UseCase is one business action. Name it with a verb phrase and give it a single `operator fun invoke`.
- A pass-through UseCase like `RefreshNotesUseCase` is fine. It keeps ViewModels independent of repositories.
- A UseCase that does CPU-heavy work gets `@DefaultDispatcher` injected and calls `withContext` itself.
- Time comes from an injected `Clock`. Never call `System.currentTimeMillis()` in logic.

## Data
```kotlin
@Serializable
internal data class NoteDto(
    val id: String,
    val title: String,
    val body: String = "",
    @SerialName("updated_at") val updatedAt: Long,
)

@Entity(tableName = "notes")
internal data class NoteEntity(@PrimaryKey val id: String, val title: String, val body: String, val updatedAt: Long)

internal fun NoteDto.toEntity() = NoteEntity(id = id, title = title, body = body, updatedAt = updatedAt)

internal fun NoteEntity.toDomain() =
    Note(id = id, title = title, body = body, updatedAt = Instant.ofEpochMilli(updatedAt))

internal interface NoteApi {
    @GET("v1/notes")
    suspend fun getNotes(): List<NoteDto>
}

@Dao
internal interface NoteDao {
    @Query("SELECT * FROM notes")
    fun observeAll(): Flow<List<NoteEntity>>

    @Upsert
    suspend fun upsertAll(notes: List<NoteEntity>)
}
```

```kotlin
internal suspend fun <T> safeApiCall(call: suspend () -> T): AppResult<T> =
    try {
        AppResult.Success(call())
    } catch (e: IOException) {
        AppResult.Failure(AppError.Network)
    } catch (e: HttpException) {
        AppResult.Failure(e.toAppError())
    } catch (e: SerializationException) {
        AppResult.Failure(AppError.Unknown(e))
    }

private fun HttpException.toAppError(): AppError = when (code()) {
    HttpURLConnection.HTTP_UNAUTHORIZED -> AppError.Unauthorized
    HttpURLConnection.HTTP_NOT_FOUND -> AppError.NotFound
    else -> AppError.Server(code())
}
```

```kotlin
// Offline-first: Room is the source of truth, and the network only refreshes it.
// Room and Retrofit are main-safe, so no withContext is needed here.
internal class NoteRepositoryImpl @Inject constructor(
    private val noteApi: NoteApi,
    private val noteDao: NoteDao,
) : NoteRepository {

    override fun observeNotes(): Flow<List<Note>> =
        noteDao.observeAll().map { entities -> entities.map(NoteEntity::toDomain) }

    override suspend fun refresh(): AppResult<Unit> =
        when (val response = safeApiCall { noteApi.getNotes() }) {
            is AppResult.Failure -> response
            is AppResult.Success -> {
                noteDao.upsertAll(response.data.map(NoteDto::toEntity))
                AppResult.Success(Unit)
            }
        }
}
```
- Catch specific exceptions only. If you ever have to catch `Exception`, rethrow `CancellationException`.
- **Cancellation is cooperative.**
  - A CPU-bound loop calls `ensureActive()` so it stops with its scope.
  - Cleanup that must finish even after cancellation runs in `withContext(NonCancellable)`.
- **Shared mutable state** in suspend code is guarded by a `Mutex`, or held in a `MutableStateFlow` and changed with `update { }`.
- The Json instance is configured with `ignoreUnknownKeys = true`, so newer backends don't break older apps.

## Dependency injection
```kotlin
@Module
@InstallIn(SingletonComponent::class)
internal abstract class NoteDataModule {
    @Binds
    abstract fun bindNoteRepository(impl: NoteRepositoryImpl): NoteRepository
}

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}
```

## Presentation: state and ViewModel
```kotlin
sealed interface NotesUiState {
    data object Loading : NotesUiState
    data object Empty : NotesUiState
    data class Success(val notes: List<Note>) : NotesUiState
    data class Error(@StringRes val messageRes: Int) : NotesUiState
}

sealed interface NotesAction {
    data object Refresh : NotesAction
}

sealed interface NotesEvent {
    data class ShowMessage(@StringRes val messageRes: Int) : NotesEvent
}

@HiltViewModel
class NotesViewModel @Inject constructor(
    observeNotes: ObserveNotesUseCase,
    private val refreshNotes: RefreshNotesUseCase,
) : ViewModel() {

    private val refreshResult = MutableStateFlow<AppResult<Unit>?>(null) // null while refreshing

    val uiState: StateFlow<NotesUiState> = combine(observeNotes(), refreshResult) { notes, refresh ->
        when {
            notes.isNotEmpty() -> NotesUiState.Success(notes)
            refresh == null -> NotesUiState.Loading
            refresh is AppResult.Failure -> NotesUiState.Error(refresh.error.toMessageRes())
            else -> NotesUiState.Empty
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(STOP_TIMEOUT_MS), NotesUiState.Loading)

    private val _events = MutableSharedFlow<NotesEvent>()
    val events: SharedFlow<NotesEvent> = _events.asSharedFlow()

    init {
        refresh()
    }

    fun onAction(action: NotesAction) {
        when (action) {
            NotesAction.Refresh -> refresh()
        }
    }

    private fun refresh() {
        viewModelScope.launch {
            refreshResult.value = null
            val result = refreshNotes()
            refreshResult.value = result
            // Cached notes stay on screen, so tell the user the refresh failed.
            if (result is AppResult.Failure && uiState.value is NotesUiState.Success) {
                _events.emit(NotesEvent.ShowMessage(result.error.toMessageRes()))
            }
        }
    }

    private companion object {
        const val STOP_TIMEOUT_MS = 5_000L
    }
}

@StringRes
fun AppError.toMessageRes(): Int = when (this) {
    AppError.Network -> R.string.error_network
    AppError.Unauthorized -> R.string.error_session_expired
    AppError.NotFound -> R.string.error_not_found
    is AppError.Server, is AppError.Unknown -> R.string.error_generic
}
```
- **State vs events.** Anything that must not be lost belongs in `UiState`. Use events only for transient UI such as snackbars. A `SharedFlow` drops events emitted while nobody is collecting.
- **Navigation** is a callback from the screen to the nav graph, not a ViewModel event.
- **Process death.**
  - Route arguments are read with `savedStateHandle.toRoute<NoteDetailRoute>()`.
  - Text the user is typing lives in `savedStateHandle.getStateFlow(KEY_DRAFT, "")`.
- **UI models.** Map to a separate UI model (e.g. `NoteItem` with a formatted date) only when the screen needs formatting. Otherwise, render the domain model.

## Presentation: Compose
```kotlin
@Composable
fun NotesScreen(
    onNoteClick: (noteId: String) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: NotesViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current
    ObserveEvents(viewModel.events) { event ->
        when (event) {
            is NotesEvent.ShowMessage -> snackbarHostState.showSnackbar(context.getString(event.messageRes))
        }
    }
    NotesContent(
        uiState = uiState,
        snackbarHostState = snackbarHostState,
        onAction = viewModel::onAction,
        onNoteClick = onNoteClick,
        modifier = modifier,
    )
}

@Composable
fun NotesContent(
    uiState: NotesUiState,
    snackbarHostState: SnackbarHostState,
    onAction: (NotesAction) -> Unit,
    onNoteClick: (noteId: String) -> Unit,
    modifier: Modifier = Modifier,
) {
    Scaffold(modifier = modifier, snackbarHost = { SnackbarHost(snackbarHostState) }) { innerPadding ->
        val contentModifier = Modifier.padding(innerPadding)
        when (uiState) {
            NotesUiState.Loading -> LoadingIndicator(modifier = contentModifier)
            NotesUiState.Empty -> EmptyState(messageRes = R.string.notes_empty, modifier = contentModifier)
            is NotesUiState.Error -> ErrorState(
                messageRes = uiState.messageRes,
                onRetry = { onAction(NotesAction.Refresh) },
                modifier = contentModifier,
            )
            is NotesUiState.Success -> NoteList(notes = uiState.notes, onNoteClick = onNoteClick, modifier = contentModifier)
        }
    }
}

@Composable
private fun NoteList(notes: List<Note>, onNoteClick: (noteId: String) -> Unit, modifier: Modifier = Modifier) {
    LazyColumn(modifier = modifier) {
        items(items = notes, key = Note::id) { note ->
            NoteRow(note = note, onClick = { onNoteClick(note.id) })
        }
    }
}

@PreviewLightDark
@Composable
private fun NotesContentPreview(@PreviewParameter(NotesUiStatePreviewProvider::class) uiState: NotesUiState) {
    AppTheme {
        NotesContent(uiState, remember { SnackbarHostState() }, onAction = {}, onNoteClick = {})
    }
}

internal class NotesUiStatePreviewProvider : PreviewParameterProvider<NotesUiState> {
    override val values = sequenceOf(
        NotesUiState.Loading,
        NotesUiState.Empty,
        NotesUiState.Error(R.string.error_network),
        NotesUiState.Success(listOf(Note(id = "1", title = "Groceries", body = "Milk", updatedAt = Instant.EPOCH))),
    )
}
```
- **Two Composables per screen.**
  - The **stateful** one (`…Screen`) gets the ViewModel and collects with `collectAsStateWithLifecycle`.
  - The **stateless** one (`…Content`) takes state plus lambdas. Previews and UI tests use it.
  - Never pass a ViewModel down to child Composables.
- **`modifier: Modifier = Modifier`** is the first optional parameter, and it's applied to the root element only.
- **Shared components:** `LoadingIndicator`, `EmptyState` and `ErrorState` come from the design system.
- **Literals** are allowed in preview data only.

Lifecycle-aware event collection, in `core:ui`:
```kotlin
@Composable
fun <T> ObserveEvents(events: Flow<T>, onEvent: suspend (T) -> Unit) {
    val lifecycleOwner = LocalLifecycleOwner.current
    val currentOnEvent by rememberUpdatedState(onEvent)
    LaunchedEffect(events, lifecycleOwner) {
        lifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            events.collect { currentOnEvent(it) }
        }
    }
}
```

## Navigation (type-safe)
```kotlin
@Serializable data object NotesRoute

@Serializable data class NoteDetailRoute(val noteId: String)

fun NavGraphBuilder.notesScreen(onNoteClick: (noteId: String) -> Unit) {
    composable<NotesRoute> { NotesScreen(onNoteClick = onNoteClick) }
}

fun NavController.navigateToNoteDetail(noteId: String) = navigate(NoteDetailRoute(noteId))

// In app: NavHost(navController, startDestination = NotesRoute) {
//     notesScreen(onNoteClick = navController::navigateToNoteDetail)
// }
```

## Instead of … write …
| Instead of | Write |
|---|---|
| `collectAsState()` | `collectAsStateWithLifecycle()` |
| `LiveData` in new code | `StateFlow` for state, `SharedFlow` for transient events |
| A public `MutableStateFlow` | A private mutable flow exposed as a read-only `StateFlow` |
| `GlobalScope.launch`, `runBlocking` | `viewModelScope`, `suspend` functions, WorkManager |
| `Dispatchers.IO` hard-coded in a class | An injected `@IoDispatcher` |
| `x!!` | `requireNotNull(x) { "…" }`, `?.`, `?:` |
| `Text("Save")` | `Text(stringResource(R.string.save))` |
| A repository injected into a ViewModel | A UseCase |
| `catch (e: Exception)` around suspend calls | Catch specific exceptions; rethrow `CancellationException` |
| `LaunchedEffect(Unit)` that reads changing inputs | Key the effect on those inputs |
| An `else` branch in a `when` over a sealed type | One branch per subtype |

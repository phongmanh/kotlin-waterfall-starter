# Code patterns

This is the canonical Kotlin (and the little Swift) for each concern in a Compose Multiplatform app. When new code follows these shapes, every feature reads the same on both platforms, and a reviewer can compare a PR against this one page. The project's own rules override it. Imports are omitted. The example feature is a notes list; everything is in `commonMain` unless a comment names another source set.

## Kotlin style
- **Immutability:** `val` over `var`; read-only collection types (`List`, not `MutableList`) in public APIs.
- **Null safety:** no `!!`. Use `?.`, `?:` or `requireNotNull(x) { "reason" }`, or redesign so the value can't be null.
- **Types:**
  - `data class` for models;
  - `sealed interface` for states, actions, events and errors;
  - a `when` over a sealed type lists every subtype, with no `else`.
- **Common code is not JVM code.** No `java.*`, `String.format`, `synchronized` or `Thread` in `commonMain`. Use `kotlin.time`, string resources with placeholders, `Mutex` and coroutines.
- **Functions:** one job each, under ~30 lines. Use expression bodies when they fit on one line.
- **Names say what, not how:** `observeNotes()`, `RefreshNotesUseCase`, `NotesUiState`. Booleans read as questions: `isLoading`, `hasMore`.
- **Named arguments** for booleans and for parameters of the same type: `Note(id = id, title = title, …)`.
- **No magic values:** `private const val` for constants; `composeResources` for anything the user sees.
- **Visibility:** `internal` by default in modules, `private` within files. Only what Swift or another module needs is public.
- **Comments** explain *why*, never *what*. KDoc only on public APIs that aren't obvious.

## Domain (pure common Kotlin)
```kotlin
data class Note(val id: String, val title: String, val body: String, val updatedAt: Instant) // kotlin.time.Instant

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

data class AppDispatchers(val io: CoroutineDispatcher, val default: CoroutineDispatcher)

interface NoteRepository {
    fun observeNotes(): Flow<List<Note>>
    suspend fun refresh(): AppResult<Unit>
}

class ObserveNotesUseCase(private val noteRepository: NoteRepository) {
    operator fun invoke(): Flow<List<Note>> =
        noteRepository.observeNotes().map { notes -> notes.sortedByDescending(Note::updatedAt) }
}

class RefreshNotesUseCase(private val noteRepository: NoteRepository) {
    suspend operator fun invoke(): AppResult<Unit> = noteRepository.refresh()
}
```
- One UseCase is one business action. Name it with a verb phrase and give it a single `operator fun invoke`.
- A pass-through UseCase like `RefreshNotesUseCase` is fine. It keeps ViewModels independent of repositories.
- No DI annotations: Koin wires constructors from the outside.
- A UseCase that does CPU-heavy work gets `AppDispatchers` injected and calls `withContext(dispatchers.default)` itself.
- Time comes from an injected `kotlin.time.Clock`. Never read the system clock in logic.

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
    Note(id = id, title = title, body = body, updatedAt = Instant.fromEpochMilliseconds(updatedAt))
```

### Network (Ktor)
```kotlin
internal fun createHttpClient(engine: HttpClientEngine, config: AppConfig, json: Json): HttpClient =
    HttpClient(engine) {
        expectSuccess = true // non-2xx responses throw ResponseException
        install(ContentNegotiation) { json(json) }
        install(HttpTimeout) { requestTimeoutMillis = REQUEST_TIMEOUT_MS }
        defaultRequest { url(config.baseUrl) } // the base URL ends with "/"
    }

private const val REQUEST_TIMEOUT_MS = 15_000L

internal class NoteApi(private val httpClient: HttpClient) {
    suspend fun getNotes(): List<NoteDto> = httpClient.get("v1/notes").body()
}

internal suspend fun <T> safeApiCall(call: suspend () -> T): AppResult<T> =
    try {
        AppResult.Success(call())
    } catch (e: ResponseException) {
        AppResult.Failure(e.response.status.toAppError())
    } catch (e: IOException) { // kotlinx.io: no connection or a timeout, on both the OkHttp and Darwin engines
        AppResult.Failure(AppError.Network)
    } catch (e: ContentConvertException) { // malformed JSON
        AppResult.Failure(AppError.Unknown(e))
    }

private fun HttpStatusCode.toAppError(): AppError = when (this) {
    HttpStatusCode.Unauthorized -> AppError.Unauthorized
    HttpStatusCode.NotFound -> AppError.NotFound
    else -> AppError.Server(value)
}
```
- The engine is injected (OkHttp on Android, Darwin on iOS, `MockEngine` in tests), so the same client code runs everywhere.
- Catch specific exceptions only. If you ever have to catch `Exception`, rethrow `CancellationException`.
- The `Json` instance is configured with `ignoreUnknownKeys = true`, so newer backends don't break older apps.
- Auth: Ktor's `Auth` plugin with `bearer { loadTokens { … }; refreshTokens { … } }`, reading tokens from the `SecureStore`. A failed refresh signs the user out.

### Database (Room KMP)
```kotlin
@Dao
internal interface NoteDao {
    @Query("SELECT * FROM notes")
    fun observeAll(): Flow<List<NoteEntity>>

    @Upsert
    suspend fun upsertAll(notes: List<NoteEntity>)
}

@Database(entities = [NoteEntity::class], version = 1)
@ConstructedBy(AppDatabaseConstructor::class)
internal abstract class AppDatabase : RoomDatabase() {
    abstract fun noteDao(): NoteDao
}

// The Room compiler generates the actual implementations.
@Suppress("KotlinNoActualForExpect")
internal expect object AppDatabaseConstructor : RoomDatabaseConstructor<AppDatabase> {
    override fun initialize(): AppDatabase
}

internal const val DATABASE_NAME = "app.db"

internal fun createDatabase(builder: RoomDatabase.Builder<AppDatabase>, dispatchers: AppDispatchers): AppDatabase =
    builder
        .setDriver(BundledSQLiteDriver())
        .setQueryCoroutineContext(dispatchers.io)
        .build()
```
```kotlin
// androidMain: Database.android.kt
internal fun databaseBuilder(context: Context): RoomDatabase.Builder<AppDatabase> {
    val appContext = context.applicationContext
    return Room.databaseBuilder<AppDatabase>(
        context = appContext,
        name = appContext.getDatabasePath(DATABASE_NAME).absolutePath,
    )
}

// iosMain: Database.ios.kt
internal fun databaseBuilder(): RoomDatabase.Builder<AppDatabase> =
    Room.databaseBuilder<AppDatabase>(name = "${applicationSupportDirectory()}/$DATABASE_NAME")

// iosMain: Files.ios.kt
// Application Support, not Documents: app data that the Files app doesn't show.
@OptIn(ExperimentalForeignApi::class)
internal fun applicationSupportDirectory(): String {
    val url = NSFileManager.defaultManager.URLForDirectory(
        directory = NSApplicationSupportDirectory,
        inDomain = NSUserDomainMask,
        appropriateForURL = null,
        create = true,
        error = null,
    )
    return requireNotNull(url?.path) { "Application Support directory is unavailable" }
}
```
- DAO functions are `suspend` or return `Flow`. Blocking DAO functions don't compile for iOS.
- The KSP compiler is added for every target (`kspAndroid`, `kspIosArm64`, `kspIosSimulatorArm64`), and `room { schemaDirectory(…) }` exports the schemas.
- If the Room version in use can't generate an `internal` constructor, make the database class, its constructor and the DAOs public.

### Key-value storage (DataStore)
```kotlin
internal const val SETTINGS_FILE = "settings.preferences_pb"

internal fun createDataStore(producePath: () -> String): DataStore<Preferences> =
    PreferenceDataStoreFactory.createWithPath(produceFile = { producePath().toPath() })
```
Bound as a `single` per file in each `platformModule` (see below). Two DataStore instances on the same file corrupt it.

### Repository
```kotlin
// Offline-first: Room is the source of truth, and the network only refreshes it.
// Ktor and Room are main-safe, so no withContext is needed here.
internal class NoteRepositoryImpl(
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

## Platform code
A platform service is an interface in `commonMain` with one implementation per platform:
```kotlin
interface SecureStore {
    suspend fun put(key: String, value: String)
    suspend fun get(key: String): String?
    suspend fun remove(key: String)
}
```
Each platform binds its implementations in its own Koin module:
```kotlin
// commonMain
internal expect val platformModule: Module

// androidMain: PlatformModule.android.kt
internal actual val platformModule = module {
    single<HttpClientEngine> { OkHttp.create() }
    single { databaseBuilder(androidContext()) }
    single { createDataStore { androidContext().filesDir.resolve(SETTINGS_FILE).absolutePath } }
    single<SecureStore> { KeystoreSecureStore(androidContext()) }
    single<SyncScheduler> { WorkManagerSyncScheduler(androidContext()) }
}

// iosMain: PlatformModule.ios.kt
internal actual val platformModule = module {
    single<HttpClientEngine> { Darwin.create() }
    single { databaseBuilder() }
    single { createDataStore { "${applicationSupportDirectory()}/$SETTINGS_FILE" } }
    single<SecureStore> { KeychainSecureStore() }
    single<SyncScheduler> { BackgroundTaskSyncScheduler() }
}
```
How each implementation protects data is in [security-privacy.md](security-privacy.md#masvs-storage).

### Swift implementation of a Kotlin interface
For an SDK that only has a Swift API:
```kotlin
// commonMain
interface AnalyticsTracker {
    fun track(event: String, params: Map<String, String>)
}

// iosMain: KoinIos.kt. Swift calls KoinIosKt.doInitKoinIos(config:analyticsTracker:)
fun initKoinIos(config: AppConfig, analyticsTracker: AnalyticsTracker) {
    initKoin(config) {
        modules(module { single { analyticsTracker } })
    }
}
```
```swift
// iosApp/FirebaseAnalyticsTracker.swift
import FirebaseAnalytics
import Shared

final class FirebaseAnalyticsTracker: NSObject, AnalyticsTracker {
    func track(event: String, params: [String: String]) {
        Analytics.logEvent(event, parameters: params)
    }
}
```
Android binds its own `AnalyticsTracker` implementation in `platformModule`.

## Dependency injection (Koin)
```kotlin
data class AppConfig(val baseUrl: String, val isDebug: Boolean)

internal val coreModule = module {
    single { AppDispatchers(io = Dispatchers.IO, default = Dispatchers.Default) }
    single<Clock> { Clock.System }
    single { Json { ignoreUnknownKeys = true } }
    single { createHttpClient(engine = get(), config = get(), json = get()) }
    single { createDatabase(builder = get(), dispatchers = get()) }
}

internal val notesModule = module {
    single { get<AppDatabase>().noteDao() }
    singleOf(::NoteApi)
    singleOf(::NoteRepositoryImpl) bind NoteRepository::class
    factoryOf(::ObserveNotesUseCase)
    factoryOf(::RefreshNotesUseCase)
    viewModelOf(::NotesViewModel)
}

fun initKoin(config: AppConfig, platformDeclaration: KoinAppDeclaration = {}) {
    startKoin {
        platformDeclaration()
        modules(module { single { config } }, platformModule, coreModule, notesModule)
    }
}
```
- `AppConfig` is public because the Android and iOS entry points build it.
- In layout B, each feature and core module owns its Koin module, and the umbrella module lists them in `initKoin`.

## Presentation: state and ViewModel
```kotlin
sealed interface NotesUiState {
    data object Loading : NotesUiState
    data object Empty : NotesUiState
    data class Success(val notes: List<Note>) : NotesUiState
    data class Error(val message: StringResource) : NotesUiState
}

sealed interface NotesAction {
    data object Refresh : NotesAction
}

sealed interface NotesEvent {
    data class ShowMessage(val message: StringResource) : NotesEvent
}

class NotesViewModel(
    observeNotes: ObserveNotesUseCase,
    private val refreshNotes: RefreshNotesUseCase,
) : ViewModel() {

    private val refreshResult = MutableStateFlow<AppResult<Unit>?>(null) // null while refreshing

    val uiState: StateFlow<NotesUiState> = combine(observeNotes(), refreshResult) { notes, refresh ->
        when {
            notes.isNotEmpty() -> NotesUiState.Success(notes)
            refresh == null -> NotesUiState.Loading
            refresh is AppResult.Failure -> NotesUiState.Error(refresh.error.toMessage())
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
                _events.emit(NotesEvent.ShowMessage(result.error.toMessage()))
            }
        }
    }

    private companion object {
        const val STOP_TIMEOUT_MS = 5_000L
    }
}

fun AppError.toMessage(): StringResource = when (this) {
    AppError.Network -> Res.string.error_network
    AppError.Unauthorized -> Res.string.error_session_expired
    AppError.NotFound -> Res.string.error_not_found
    is AppError.Server, is AppError.Unknown -> Res.string.error_generic
}
```
- **State vs events.** Anything that must not be lost belongs in `UiState`. Use events only for transient UI such as snackbars. A `SharedFlow` drops events emitted while nobody is collecting.
- **Messages are `StringResource`s,** resolved in the UI. The ViewModel never holds a formatted, locale-specific string.
- **Navigation** is a callback from the screen to the nav graph, not a ViewModel event.
- **Arguments** come in through Koin parameters (`koinViewModel { parametersOf(noteId) }`), taken from the typed route in the nav graph.
- **Drafts.** Text the user is typing is saved to local storage (e.g. a drafts table), not only to `SavedStateHandle`: iOS doesn't restore saved state after the app is terminated.
- **UI models.** Map to a separate UI model (e.g. `NoteItem` with a formatted date) only when the screen needs formatting. Otherwise, render the domain model.

## Presentation: Compose
```kotlin
@Composable
fun NotesScreen(
    onNoteClick: (noteId: String) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: NotesViewModel = koinViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }
    ObserveEvents(viewModel.events) { event ->
        when (event) {
            is NotesEvent.ShowMessage -> snackbarHostState.showSnackbar(getString(event.message))
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
            NotesUiState.Empty -> EmptyState(message = Res.string.notes_empty, modifier = contentModifier)
            is NotesUiState.Error -> ErrorState(
                message = uiState.message,
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

@Preview
@Composable
private fun NotesContentPreview(@PreviewParameter(NotesUiStatePreviewProvider::class) uiState: NotesUiState) {
    AppTheme {
        NotesContent(uiState, remember { SnackbarHostState() }, onAction = {}, onNoteClick = {})
    }
}

@Preview
@Composable
private fun NotesContentDarkPreview() {
    AppTheme(darkTheme = true) {
        NotesContent(NotesUiState.Empty, remember { SnackbarHostState() }, onAction = {}, onNoteClick = {})
    }
}

internal class NotesUiStatePreviewProvider : PreviewParameterProvider<NotesUiState> {
    override val values = sequenceOf(
        NotesUiState.Loading,
        NotesUiState.Empty,
        NotesUiState.Error(Res.string.error_network),
        NotesUiState.Success(
            listOf(Note(id = "1", title = "Groceries", body = "Milk", updatedAt = Instant.fromEpochMilliseconds(0))),
        ),
    )
}
```
- **Two Composables per screen.**
  - The **stateful** one (`…Screen`) gets the ViewModel from `koinViewModel()` and collects with `collectAsStateWithLifecycle`.
  - The **stateless** one (`…Content`) takes state plus lambdas. Previews and UI tests use it.
  - Never pass a ViewModel down to child Composables.
- **`modifier: Modifier = Modifier`** is the first optional parameter, and it's applied to the root element only.
- **Shared components:** `LoadingIndicator`, `EmptyState` and `ErrorState` come from the design system and take `StringResource`s.
- **Previews in `commonMain`** use the multiplatform `@Preview`. Android-only multipreviews (`@PreviewLightDark`, `@PreviewFontScale`) don't exist there, so write the dark and large-font variants explicitly.
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

fun NavGraphBuilder.noteDetailScreen(onBack: () -> Unit) {
    composable<NoteDetailRoute> { entry ->
        val route = entry.toRoute<NoteDetailRoute>()
        NoteDetailScreen(noteId = route.noteId, onBack = onBack)
    }
}

fun NavController.navigateToNoteDetail(noteId: String) = navigate(NoteDetailRoute(noteId))

@Composable
fun App() {
    AppTheme {
        val navController = rememberNavController()
        NavHost(navController, startDestination = NotesRoute) {
            notesScreen(onNoteClick = navController::navigateToNoteDetail)
            noteDetailScreen(onBack = { navController.popBackStack() })
        }
    }
}
```
- `NoteDetailScreen` takes `onBack` and shows a back button in its top bar: iOS has no system back button.
- Deep links from App Links and Universal Links are parsed and validated in one common function, then navigated with the same typed routes.

## Entry points
```kotlin
// androidApp: NotesApplication.kt
class NotesApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin(AppConfig(baseUrl = BuildConfig.BASE_URL, isDebug = BuildConfig.DEBUG)) {
            androidContext(this@NotesApplication)
        }
    }
}

// androidApp: MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}

// shared/iosMain: MainViewController.kt. Swift calls MainViewControllerKt.MainViewController()
fun MainViewController(): UIViewController = ComposeUIViewController { App() }
```
```swift
// iosApp/iOSApp.swift
import SwiftUI
import Shared

@main
struct iOSApp: App {
    init() {
        guard let baseUrl = Bundle.main.object(forInfoDictionaryKey: "BASE_URL") as? String else {
            fatalError("BASE_URL is missing from Info.plist")
        }
        #if DEBUG
        let isDebug = true
        #else
        let isDebug = false
        #endif
        // Native SDK set-up (e.g. FirebaseApp.configure()) goes before Koin starts.
        KoinIosKt.doInitKoinIos(
            config: AppConfig(baseUrl: baseUrl, isDebug: isDebug),
            analyticsTracker: FirebaseAnalyticsTracker()
        )
    }

    var body: some Scene {
        WindowGroup {
            ComposeView().ignoresSafeArea() // Compose applies the safe-area insets itself
        }
    }
}

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
```

## Instead of … write …
| Instead of | Write |
|---|---|
| `java.time.Instant`, `System.currentTimeMillis()` | `kotlin.time.Instant`, an injected `Clock` |
| `R.string.x`, `@StringRes Int` | `Res.string.x`, `StringResource` |
| `String.format(…)` or string concatenation for UI text | A string resource with `%1$s` placeholders: `stringResource(Res.string.x, arg)` |
| `@Inject`, `@HiltViewModel`, `hiltViewModel()` | Plain constructors, a Koin module, `koinViewModel()` |
| Retrofit or OkHttp interceptors in shared code | Ktor client and its plugins |
| `java.io.IOException` | `kotlinx.io.IOException` |
| `Dispatchers.IO` hard-coded in a class | An injected `AppDispatchers` |
| `expect class` for a service | An interface in `commonMain`, implemented per platform and bound with Koin |
| `if (platform == Platform.IOS)` in a screen | A design-system component or an `expect` Composable |
| `Log.d`, `println`, `NSLog` | Kermit's `Logger` |
| `collectAsState()` | `collectAsStateWithLifecycle()` |
| A public `MutableStateFlow` | A private mutable flow exposed as a read-only `StateFlow` |
| `GlobalScope.launch`, `runBlocking` | `viewModelScope`, `suspend` functions, the `SyncScheduler` |
| `x!!` | `requireNotNull(x) { "…" }`, `?.`, `?:` |
| `Text("Save")` | `Text(stringResource(Res.string.save))` |
| A repository injected into a ViewModel | A UseCase |
| `catch (e: Exception)` around suspend calls | Catch specific exceptions; rethrow `CancellationException` |
| `LaunchedEffect(Unit)` that reads changing inputs | Key the effect on those inputs |
| An `else` branch in a `when` over a sealed type | One branch per subtype |
| Public declarations by default in shared modules | `internal`, so the iOS header stays small |

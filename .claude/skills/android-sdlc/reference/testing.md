# Testing reference

## Pyramid
| Level | Share (e.g.) | Runs on | Covers |
|---|---|---|---|
| Unit | ~70% | JVM, on every PR | UseCases, mappers, repositories with fakes, ViewModels |
| Integration | ~20% | JVM (Robolectric) or a device | Room DAOs and migrations, the API with MockWebServer, DI wiring |
| UI and screenshot | ~10% | JVM for screenshots; a device for UI tests | Critical flows, design-system components, key screens |
| System and NFR | Per the test plan | Device matrix, release build | End to end, performance, accessibility, security, upgrade |

## What to test in each layer
| Layer | Test | Test doubles |
|---|---|---|
| Domain | Every UseCase: the happy path, each error, the edge cases | Fake repositories |
| Data | Repositories map DTOs, handle each error and write to the database; DAO queries; migrations | MockWebServer or a fake API; in-memory Room |
| Presentation | ViewModels: the initial state, the state after each action, how errors become messages | Fake repositories behind real UseCases; `MainDispatcherRule` |
| UI | The stateless `…Content` renders each state, and clicks call the right callback | A fixed `UiState` |

## Conventions
- **Files.** Name the file `<ClassUnderTest>Test.kt`, in the same package as the class under test.
- **Test names** describe the behaviour.
  - JVM tests use backtick names: `` `refresh fails offline - shows network error`() ``.
  - Instrumented tests use `action_condition_result` names, because DEX doesn't allow spaces before API 30.
- **Structure.** Arrange–Act–Assert, one behaviour per test, and no logic (`if`, loops) in tests.
- **Fakes over mocks.** A `FakeNoteRepository` in the testing module is reused by every test and survives refactors. Use MockK only for what you can't fake.
- **Deterministic.**
  - Inject `CoroutineDispatcher` and `Clock`, and use `runTest`.
  - Never `Thread.sleep`, never the real network.
- **Test data builders** with defaults keep tests short: `aNote(title = "x")`.
- **Coverage.** Kover enforces a floor (e.g. ≥ 80% of lines in domain and ViewModels). Coverage is a floor, not the goal.

## Snippets
Shared test infrastructure, in `core:testing` or a `testFixtures` source set:
```kotlin
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher(),
) : TestWatcher() {
    override fun starting(description: Description) = Dispatchers.setMain(dispatcher)
    override fun finished(description: Description) = Dispatchers.resetMain()
}

class FakeNoteRepository : NoteRepository {
    val notes = MutableStateFlow<List<Note>>(emptyList())
    var refreshResult: AppResult<Unit> = AppResult.Success(Unit)

    override fun observeNotes(): Flow<List<Note>> = notes
    override suspend fun refresh(): AppResult<Unit> = refreshResult
}
```

A ViewModel test with Turbine:
```kotlin
class NotesViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val repository = FakeNoteRepository()

    @Test
    fun `no notes and refresh succeeds - shows empty state`() = runTest {
        val viewModel = createViewModel()

        viewModel.uiState.test {
            assertEquals(NotesUiState.Loading, awaitItem())
            assertEquals(NotesUiState.Empty, awaitItem())
        }
    }

    @Test
    fun `no notes and refresh fails offline - shows network error`() = runTest {
        repository.refreshResult = AppResult.Failure(AppError.Network)
        val viewModel = createViewModel()

        viewModel.uiState.test {
            assertEquals(NotesUiState.Loading, awaitItem())
            assertEquals(NotesUiState.Error(R.string.error_network), awaitItem())
        }
    }

    // Created inside each test, after MainDispatcherRule has set Dispatchers.Main.
    private fun createViewModel() =
        NotesViewModel(ObserveNotesUseCase(repository), RefreshNotesUseCase(repository))
}
```

A Room DAO test with Robolectric or on a device. Repository tests follow the same shape: put MockWebServer behind a real Retrofit instance, enqueue each response type (success, 401, 500, malformed JSON), and assert the returned `AppResult` and the database contents.
```kotlin
@RunWith(AndroidJUnit4::class)
class NoteDaoTest {
    private lateinit var database: AppDatabase
    private lateinit var noteDao: NoteDao

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        noteDao = database.noteDao()
    }

    @After
    fun tearDown() = database.close()

    @Test
    fun upsertAll_existingId_replacesNote() = runTest {
        noteDao.upsertAll(listOf(aNoteEntity(id = "1", title = "Old")))
        noteDao.upsertAll(listOf(aNoteEntity(id = "1", title = "New")))

        assertEquals(listOf("New"), noteDao.observeAll().first().map(NoteEntity::title))
    }
}
```

A Compose UI test against the stateless content:
```kotlin
class NotesContentTest {
    @get:Rule
    val composeRule = createAndroidComposeRule<ComponentActivity>()

    @Test
    fun errorState_clickRetry_sendsRefresh() {
        val actions = mutableListOf<NotesAction>()
        composeRule.setContent {
            AppTheme {
                NotesContent(
                    uiState = NotesUiState.Error(R.string.error_network),
                    snackbarHostState = remember { SnackbarHostState() },
                    onAction = actions::add,
                    onNoteClick = {},
                )
            }
        }

        composeRule.onNodeWithText(composeRule.activity.getString(R.string.retry)).performClick()

        assertEquals(listOf<NotesAction>(NotesAction.Refresh), actions)
    }
}
```
- Find nodes by text or content description, the same way TalkBack users do. Use `testTag` only when nothing user-visible identifies the node.
- If the project uses the Compose accessibility test artifact, call `composeRule.enableAccessibilityChecks()`, so UI tests also catch accessibility issues.

## Screenshot tests
- **What:** design-system components, plus each key screen in each `UiState`, in light and dark and at a large font. Reuse the `@Preview`s.
- **Tools:** either one, chosen in an ADR.
  - Roborazzi: runs on the JVM with Robolectric and can capture previews automatically.
  - Compose Preview Screenshot Testing: a `screenshotTest` source set.
- **Process.** Commit the reference images. A failed comparison is reviewed like a code diff.

## Commands
| Purpose | Command |
|---|---|
| JVM unit and Robolectric tests | `./gradlew test` |
| Instrumented tests on a connected device | `./gradlew connectedDebugAndroidTest` |
| Coverage report and floor | `./gradlew koverHtmlReport koverVerify` |
| Screenshots with Roborazzi (record / verify) | `./gradlew recordRoborazziDebug` / `verifyRoborazziDebug` |
| Screenshots with Compose Preview Screenshot Testing (update / validate) | `./gradlew updateDebugScreenshotTest` / `validateDebugScreenshotTest` |
| Baseline Profile | `./gradlew :app:generateBaselineProfile` |
| Macrobenchmarks | `./gradlew :benchmark:connectedCheck` |

# Testing reference

Shared code is tested once in `commonTest`, and that suite runs on both platforms: on the JVM (fast, every PR) and on the iOS simulator (macOS CI). Platform code is tested on its own platform.

## Pyramid
| Level | Share (e.g.) | Runs on | Covers |
|---|---|---|---|
| Unit | ~70% | `commonTest` on the JVM on every PR; on the iOS simulator on every PR or nightly | UseCases, mappers, repositories with fakes, ViewModels |
| Integration | ~20% | `commonTest` plus platform test source sets | Room DAOs and migrations, the API with Ktor `MockEngine`, the DI graph, platform service implementations |
| UI and screenshot | ~10% | Common Compose UI tests on the iOS simulator and an Android device; screenshots on the JVM | Critical flows, design-system components, key screens |
| System and NFR | Per the test plan | Android and iOS device matrix, release builds | End to end, performance, accessibility, security, upgrade |

## What to test in each layer
| Layer | Test | Test doubles | Source set |
|---|---|---|---|
| Domain | Every UseCase: the happy path, each error, the edge cases | Fake repositories | `commonTest` |
| Data | Repositories map DTOs, handle each error and write to the database; DAO queries; migrations | Ktor `MockEngine`; a fake DAO or an in-memory Room database | `commonTest`; migrations on the JVM or an Android device |
| Presentation | ViewModels: the initial state, the state after each action, how errors become messages | Fake repositories behind real UseCases; `Dispatchers.setMain` | `commonTest` |
| UI | The stateless `…Content` renders each state, and clicks call the right callback | A fixed `UiState` | `commonTest` (`runComposeUiTest`) |
| Platform services | Each `actual` and each platform implementation (`KeychainSecureStore`, `WorkManagerSyncScheduler`…) | The real platform API | `androidHostTest` / `androidDeviceTest`, `iosTest` |
| DI | The Koin graph resolves every ViewModel and UseCase | Test bindings for the platform module | A JVM test |
| Swift glue | Swift implementations of Kotlin interfaces | — | XCTest in `iosApp` |

## Conventions
- **Files.** Name the file `<ClassUnderTest>Test.kt`, in the same package as the class under test.
- **Test names** describe the behaviour, as `action_condition_result`: `refresh_offline_showsNetworkError`. `commonTest` compiles for Kotlin/Native and, when device tests include it, for Android devices, where DEX doesn't allow spaces in names before API 30. Backtick names with spaces are fine only in `androidHostTest`.
- **kotlin-test, not JUnit, in common code:** `@Test`, `@BeforeTest`, `@AfterTest`, `assertEquals`. JUnit rules don't exist in `commonTest`; set and reset the Main dispatcher in `@BeforeTest`/`@AfterTest`.
- **Structure.** Arrange–Act–Assert, one behaviour per test, and no logic (`if`, loops) in tests.
- **Fakes over mocks.** MockK is JVM-only, so common tests use fakes: a `FakeNoteRepository` in the testing module is reused by every test and survives refactors. Use Mokkery only for what you can't fake.
- **Deterministic.**
  - Inject `AppDispatchers` and `Clock`, and use `runTest`.
  - Never sleep, never the real network: `MockEngine` replaces the HTTP engine.
- **Test data builders** with defaults keep tests short: `aNote(title = "x")`.
- **Coverage.** Kover enforces a floor (e.g. ≥ 80% of lines in domain and ViewModels). It measures the JVM run of common code; iOS-only code is not measured, so keep `iosMain` thin and covered by `iosTest`. Coverage is a floor, not the goal.

## Snippets
Shared test infrastructure, in `core:testing` or the module's `commonTest`:
```kotlin
class FakeNoteRepository : NoteRepository {
    val notes = MutableStateFlow<List<Note>>(emptyList())
    var refreshResult: AppResult<Unit> = AppResult.Success(Unit)

    override fun observeNotes(): Flow<List<Note>> = notes
    override suspend fun refresh(): AppResult<Unit> = refreshResult
}

internal class FakeNoteDao : NoteDao {
    val notes = MutableStateFlow<List<NoteEntity>>(emptyList())

    override fun observeAll(): Flow<List<NoteEntity>> = notes
    override suspend fun upsertAll(notes: List<NoteEntity>) {
        this.notes.value = (this.notes.value.associateBy(NoteEntity::id) + notes.associateBy(NoteEntity::id)).values.toList()
    }
}
```

A ViewModel test with Turbine:
```kotlin
class NotesViewModelTest {
    private val repository = FakeNoteRepository()

    @BeforeTest
    fun setUp() = Dispatchers.setMain(UnconfinedTestDispatcher())

    @AfterTest
    fun tearDown() = Dispatchers.resetMain()

    @Test
    fun init_noNotesAndRefreshSucceeds_showsEmptyState() = runTest {
        val viewModel = createViewModel()

        viewModel.uiState.test {
            assertEquals(NotesUiState.Loading, awaitItem())
            assertEquals(NotesUiState.Empty, awaitItem())
        }
    }

    @Test
    fun init_noNotesAndRefreshFailsOffline_showsNetworkError() = runTest {
        repository.refreshResult = AppResult.Failure(AppError.Network)
        val viewModel = createViewModel()

        viewModel.uiState.test {
            assertEquals(NotesUiState.Loading, awaitItem())
            assertEquals(NotesUiState.Error(Res.string.error_network), awaitItem())
        }
    }

    // Created inside each test, after setUp() has set Dispatchers.Main.
    private fun createViewModel() =
        NotesViewModel(ObserveNotesUseCase(repository), RefreshNotesUseCase(repository))
}
```

A repository test with Ktor's `MockEngine`, which runs unchanged on the JVM and on iOS. Enqueue each response type (success, 401, 500, malformed JSON), and assert the returned `AppResult` and what was stored:
```kotlin
class NoteRepositoryImplTest {
    private val noteDao = FakeNoteDao()

    @Test
    fun refresh_success_storesNotes() = runTest {
        val engine = MockEngine {
            respond(
                content = """[{"id":"1","title":"Groceries","updated_at":0}]""",
                headers = headersOf(HttpHeaders.ContentType, ContentType.Application.Json.toString()),
            )
        }

        createRepository(engine).refresh()

        assertEquals(listOf("Groceries"), noteDao.notes.value.map(NoteEntity::title))
    }

    @Test
    fun refresh_unauthorized_returnsUnauthorizedAndKeepsCache() = runTest {
        noteDao.notes.value = listOf(aNoteEntity(id = "1"))
        val engine = MockEngine { respondError(HttpStatusCode.Unauthorized) }

        val result = createRepository(engine).refresh()

        assertEquals(AppResult.Failure(AppError.Unauthorized), result)
        assertEquals(listOf("1"), noteDao.notes.value.map(NoteEntity::id))
    }

    private fun createRepository(engine: HttpClientEngine) = NoteRepositoryImpl(
        noteApi = NoteApi(createHttpClient(engine, AppConfig(baseUrl = BASE_URL, isDebug = true), Json { ignoreUnknownKeys = true })),
        noteDao = noteDao,
    )

    private companion object {
        const val BASE_URL = "https://api.test/"
    }
}
```

A DAO test against an in-memory Room database. The builder is an `expect fun` in `commonTest`, with an `actual` in every test source set that compiles `commonTest`:
```kotlin
// commonTest
internal expect fun inMemoryDatabaseBuilder(): RoomDatabase.Builder<AppDatabase>

class NoteDaoTest {
    private val database = inMemoryDatabaseBuilder().setDriver(BundledSQLiteDriver()).build()
    private val noteDao = database.noteDao()

    @AfterTest
    fun tearDown() = database.close()

    @Test
    fun upsertAll_existingId_replacesNote() = runTest {
        noteDao.upsertAll(listOf(aNoteEntity(id = "1", title = "Old")))
        noteDao.upsertAll(listOf(aNoteEntity(id = "1", title = "New")))

        assertEquals(listOf("New"), noteDao.observeAll().first().map(NoteEntity::title))
    }
}

// iosTest
internal actual fun inMemoryDatabaseBuilder() = Room.inMemoryDatabaseBuilder<AppDatabase>()

// androidHostTest (with Robolectric) or androidDeviceTest
internal actual fun inMemoryDatabaseBuilder() =
    Room.inMemoryDatabaseBuilder<AppDatabase>(ApplicationProvider.getApplicationContext<Context>())
```

A Compose UI test against the stateless content, in `commonTest`. It runs on the iOS simulator and on an Android device or emulator:
```kotlin
@OptIn(ExperimentalTestApi::class)
class NotesContentTest {
    @Test
    fun errorState_clickRetry_sendsRefresh() = runComposeUiTest {
        val actions = mutableListOf<NotesAction>()
        lateinit var retryLabel: String
        setContent {
            retryLabel = stringResource(Res.string.retry)
            AppTheme {
                NotesContent(
                    uiState = NotesUiState.Error(Res.string.error_network),
                    snackbarHostState = remember { SnackbarHostState() },
                    onAction = actions::add,
                    onNoteClick = {},
                )
            }
        }

        onNodeWithText(retryLabel).performClick()

        assertEquals(listOf<NotesAction>(NotesAction.Refresh), actions)
    }
}
```
- Find nodes by text or content description, the same way TalkBack and VoiceOver users do. Use `testTag` only when nothing user-visible identifies the node; on iOS a `testTag` also becomes the `accessibilityIdentifier` that XCUITest can find.
- The common UI-test API is experimental; pin the opt-in to the test classes.
- Common Compose tests don't run as Android host (JVM) tests; on Android they need a device or emulator.

**DI graph.** Koin resolves at runtime, so a JVM test starts the full graph, with the platform module replaced by test bindings (e.g. `MockEngine`, an in-memory database), and resolves every ViewModel and UseCase. Koin's `verify()` is an alternative. A missing binding then fails CI instead of crashing the app.

## Screenshot tests
- **What:** design-system components, plus each key screen in each `UiState`, in light and dark and at a large font. Reuse the `@Preview`s.
- **Tools:** Roborazzi, chosen in an ADR, runs on the JVM with Robolectric and captures the shared Composables. The layout is shared, so these images catch most visual regressions for both platforms.
- **iOS rendering differences** (fonts, safe areas, text fields) are checked in system tests on iOS devices, or with Roborazzi's experimental iOS support if the ADR adopts it.
- **Process.** Commit the reference images. A failed comparison is reviewed like a code diff.

## iOS-only tests
- **XCTest** in `iosApp` for Swift implementations of Kotlin interfaces and other Swift glue.
- **XCUITest** for a smoke test of the critical flow on a Release-configuration build, finding elements by their accessibility labels or identifiers.

## Commands
| Purpose | Command |
|---|---|
| All tests that can run on this machine (JVM; iOS simulator on macOS) | `./gradlew :shared:allTests` |
| Common and iOS tests on the iOS simulator | `./gradlew :shared:iosSimulatorArm64Test` |
| Common Compose UI tests and device tests on a connected Android device | `./gradlew :shared:connectedAndroidTest` |
| iOS app build (simulator) | `xcodebuild -project iosApp/iosApp.xcodeproj -scheme iosApp -configuration Debug -destination 'generic/platform=iOS Simulator' build` |
| XCTest / XCUITest | `xcodebuild test -project iosApp/iosApp.xcodeproj -scheme iosApp -destination 'platform=iOS Simulator,name=<device>'` |
| Coverage report and floor | `./gradlew koverHtmlReport koverVerify` |
| Screenshots with Roborazzi (record / verify) | The module's `recordRoborazzi…` / `verifyRoborazzi…` tasks (`./gradlew :shared:tasks --all` lists them) |
| Baseline Profile | `./gradlew :androidApp:generateBaselineProfile` |
| Macrobenchmarks | `./gradlew :benchmark:connectedCheck` |

In layout B, replace `:shared` with the module under test.

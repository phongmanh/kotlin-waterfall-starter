# Feature design: <Feature>

| FR IDs | Platforms | Owner | Status | UI designs |
|---|---|---|---|---|
| FR-001, FR-002 | Both | <developer> | Draft | <Figma link, including iOS adaptations> |

## 1. Screens
| Screen | Route (arguments) | States | Back affordance | Notes |
|---|---|---|---|---|
| Notes list | `NotesRoute` | Loading, Empty, Success, Error | Root: none | Snackbar when a refresh fails over cached notes |

### <Screen>: state, actions and events
```kotlin
sealed interface NotesUiState { /* Loading, Empty, Success(notes), Error(message: StringResource) */ }
sealed interface NotesAction { /* user intents sent to the ViewModel */ }
sealed interface NotesEvent { /* transient UI only, e.g. ShowMessage(message: StringResource) */ }
```
- Survives Android process death: <fields kept in SavedStateHandle>
- Survives iOS termination: <data written to local storage, e.g. drafts>

## 2. Domain
```kotlin
data class Note(val id: String, val title: String, val body: String, val updatedAt: Instant)

interface NoteRepository {
    fun observeNotes(): Flow<List<Note>>
    suspend fun refresh(): AppResult<Unit>
}

class ObserveNotesUseCase(noteRepository: NoteRepository) { operator fun invoke(): Flow<List<Note>> }
```

## 3. Data
| Endpoint | Request | Response | Errors |
|---|---|---|---|
| `GET /v1/notes` | — | `List<NoteDto>` | 401, 5xx |

- **Room:**
  - entity `NoteEntity` (`id` as the primary key; index on `updatedAt`);
  - DAO `observeAll(): Flow<List<NoteEntity>>`, `suspend fun upsertAll(…)`;
  - migration <n> → <n+1>: <SQL, or "none">.
- **DataStore keys:** <…>
- **SecureStore keys:** <…>
- **Cache and refresh:** <following the architecture's data strategy>

## 4. Platform notes
"None" is a valid answer: the feature is fully shared.

| Part | Common API | Android (`androidMain`) | iOS (`iosMain` / Swift) | Permission / usage description |
|---|---|---|---|---|
| e.g. Share a note | `ShareService.share(text)` | Share sheet intent | `UIActivityViewController` | — |

- iOS adaptations from the look-and-feel ADR: <…>
- Platform matrix change needed: <no / CR-…>

## 5. Errors
| AppError | Message (string resource) | UI behaviour |
|---|---|---|
| Network | `error_network` | Error state with Retry; or a snackbar if cached notes are shown |
| Unauthorized | `error_session_expired` | Go to sign-in |

## 6. Analytics
| Event | Parameters | Trigger |
|---|---|---|

## 7. Accessibility and i18n
- Content descriptions
- Headings
- Focus order
- New strings and plurals (`composeResources/values/strings.xml`)
- Locale-aware formatting
- RTL notes

## 8. Test cases
| ID | Level | FR | Platforms | Case |
|---|---|---|---|---|
| IT-001 | Integration | FR-001 | Both (`commonTest`) | Refresh stores the notes; the DAO emits them |
| UI-001 | UI | FR-001 | Both | Empty state shows "Create note", which opens the editor |
| IT-002 | Integration | FR-002 | iOS (`iosTest`) | `ShareService` presents the share sheet |

## 9. PR slice plan
| # | PR | Layer | Est. changed lines |
|---|---|---|---|
| 1 | Note model, repository interface, UseCases + tests | Domain | ~200 |
| 2 | Ktor API, Room, repository implementation + tests | Data | ~350 |
| 3 | Platform implementations + platform tests | Platform | ~200 |
| 4 | UiState, ViewModel + tests | Presentation | ~250 |
| 5 | Screen and content, previews, navigation, Koin | Presentation | ~300 |
| 6 | Critical-flow UI test (both platforms) | Test | ~100 |

## 10. Open questions
- <…>

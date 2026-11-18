# UI/UX reference

Aim for a clean, standard Material 3 app that is accessible and predictable. Design custom UI only where the brand or the product needs it.

## Design system
- **One theme module.** A single `core:designsystem` module (or `designsystem` package) holds `AppTheme`:
  - light and dark color schemes;
  - typography and shapes;
  - spacing tokens (e.g. `Spacing.small = 8.dp`).

  Screens use the tokens, never raw `dp` or `Color` values.
- **Dynamic color** (Android 12+) is decided in an ADR. Brand-heavy apps usually turn it off.
- **Shared components.** Build screens from components that wrap Material 3: `AppButton`, `AppTopBar`, `LoadingIndicator`, `EmptyState`, `ErrorState`. A component moves into the design system once two screens need it.
- **Icons:** Material Symbols as vector drawables. Directional icons are auto-mirrored for RTL.

## Every screen has every state
| State | Show | Next action |
|---|---|---|
| Loading | A progress indicator or skeleton, after a short delay so fast loads don't flash | — |
| Empty | A short explanation of why it's empty | A primary call to action (e.g. "Create note") |
| Error | A plain-language message from the `AppError` mapping | Retry, or sign in again for auth errors |
| Offline | Cached content plus a non-blocking banner | Retry automatically when the connection returns |
| Partial failure | The content, with an inline error for the part that failed | Retry that part |
| Permission denied | Why the permission helps, and what still works without it | Open settings, or an alternative path |

## Layout and navigation
- **Edge-to-edge** is enforced when targeting API 35+.
  - Draw behind the system bars and apply `WindowInsets` padding; `Scaffold` handles most of it.
  - Test with both gesture and 3-button navigation.
- **Predictive back.** Rely on the system back behaviour. Use `BackHandler` only for real in-screen state, such as closing a sheet.
- **Adaptive layouts.**
  - Use window size classes, with list-detail or two panes on expanded widths.
  - Don't lock the orientation unless the product needs it.
  - Test on tablets, foldables, in landscape and in multi-window.
- **Navigation structure.**
  - Bottom navigation for 3–5 top-level destinations, or a navigation rail on wide screens.
  - A top app bar with a clear title.
  - One primary action per screen.
- **Keyboard.**
  - Content scrolls above the keyboard (`imePadding`).
  - Fields set the right `KeyboardOptions` (keyboard type, IME action), plus autofill hints where useful.

## Accessibility
Covers TalkBack, Switch Access and large text.
- **Labels.** Every icon-only control has a `contentDescription` from string resources. Decorative images use `null`.
- **Touch targets** are at least 48×48 dp. Material 3 components already comply; check custom ones.
- **Contrast** is at least 4.5:1 for text, and 3:1 for large text and UI controls. Never use color alone to convey meaning.
- **Text size.** Text uses `sp`. Layouts survive 200% font scale and the largest display size without clipping, so text containers never get fixed heights.
- **Structure.**
  - Group related content with `Modifier.semantics(mergeDescendants = true)`.
  - Mark headings with `semantics { heading() }`.
  - Keep the focus order logical.
- **Announcements.** Announce important changes such as errors through live regions or snackbars, never through animation alone. Respect the system "remove animations" setting.

## Text and localisation
- **Strings.** All user-facing text lives in `strings.xml`.
  - Plurals use `pluralStringResource`.
  - Use placeholders (`%1$s`), never string concatenation.
- **Formats.** Format dates, numbers and currency for the locale. Store times in UTC and display them in local time.
- **RTL.** Use `start`/`end`, never `left`/`right`. Test with the `ar-XB` pseudo-locale.
- **Per-app language** (Android 13+): set up `localeConfig` when the app supports several languages.
- **Copy** is short and specific: say what happened and what the user can do. Example: "No connection. Showing saved notes."

## Feedback and forms
- **Confirmations.** Confirm actions with a snackbar. For a reversible destructive action, offer Undo instead of a confirmation dialog.
- **Validation.** Validate a field when the user leaves it, and show the error under the field. Disable the submit button only when a visible reason explains why.
- **Long actions.** Show progress on the button and prevent double submits.
- **Motion and haptics** are subtle, purposeful and consistent with Material 3 motion.

## Previews
- **Coverage.** Every public Composable has previews for:
  - each `UiState`;
  - light and dark (`@PreviewLightDark`);
  - large font (`@PreviewFontScale`);
  - for screens, a wide window (`@PreviewScreenSizes`).
- Use a `PreviewParameterProvider` for the state variants.
- Previews double as screenshot tests (see [testing.md](testing.md#screenshot-tests)).

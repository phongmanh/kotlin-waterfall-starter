# UI/UX reference

Aim for one clean, accessible Material 3 design system that feels at home on both platforms. Adapt to iOS conventions where users would otherwise stumble, and record those choices once in an ADR ([platform look and feel](platform-integration.md#platform-look-and-feel)). Design custom UI only where the brand or the product needs it.

## Design system
- **One theme module in `commonMain`.** A single `core:designsystem` module (or `designsystem` package) holds `AppTheme`:
  - light and dark color schemes;
  - typography and shapes, with fonts shipped as Compose resources when the brand needs them;
  - spacing tokens (e.g. `Spacing.small = 8.dp`).

  Screens use the tokens, never raw `dp` or `Color` values.
- **Dynamic color** exists on Android 12+ only. Decide in an ADR; brand-heavy apps usually turn it off so both platforms look the same.
- **Shared components.** Build screens from components that wrap Material 3: `AppButton`, `AppTopBar`, `LoadingIndicator`, `EmptyState`, `ErrorState`. A component moves into the design system once two screens need it.
- **Platform adaptation lives in components.** A difference between Android and iOS (e.g. the top bar's back affordance, a date picker) is decided inside one design-system component, never inline in screens.
- **Icons:** vector icons as Compose resources (`Res.drawable.…`). Directional icons are mirrored for RTL.

## Every screen has every state
| State | Show | Next action |
|---|---|---|
| Loading | A progress indicator or skeleton, after a short delay so fast loads don't flash | — |
| Empty | A short explanation of why it's empty | A primary call to action (e.g. "Create note") |
| Error | A plain-language message from the `AppError` mapping | Retry, or sign in again for auth errors |
| Offline | Cached content plus a non-blocking banner | Retry automatically when the connection returns |
| Partial failure | The content, with an inline error for the part that failed | Retry that part |
| Pending sync | The local change, marked as not yet synced | Sync runs on its own; offer a manual retry if it keeps failing |
| Permission denied | Why the permission helps, and what still works without it | Open settings (on iOS the only way back), or an alternative path |

## Layout and navigation
- **Edge-to-edge on both platforms.**
  - Android: `enableEdgeToEdge()`; edge-to-edge is enforced when targeting API 35+.
  - iOS: the SwiftUI host ignores the safe area, and Compose applies it (notch, Dynamic Island, home indicator).
  - `Scaffold` and `WindowInsets.safeDrawing` handle most of it. Test with gesture and 3-button navigation on Android, and on an iPhone with a Dynamic Island.
- **Back navigation.**
  - Android: rely on the system back behaviour, including predictive back. Use `BackHandler` only for real in-screen state, such as closing a sheet.
  - iOS: there is no system back button. **Every non-root screen shows a back or close control,** and the edge-swipe gesture works where the navigation library supports it.
- **Adaptive layouts.**
  - Use window size classes (`currentWindowAdaptiveInfo()`), with list-detail or two panes on expanded widths.
  - Don't lock the orientation unless the product needs it.
  - Test on Android tablets and foldables, on iPad (including Split View and Slide Over, if supported), in landscape and in multi-window.
- **Navigation structure.**
  - A bottom navigation bar for 3–5 top-level destinations (users of both platforms know it as a tab bar), or a navigation rail on wide screens.
  - A top app bar with a clear title.
  - One primary action per screen.
- **Keyboard.**
  - Content scrolls above the keyboard (`imePadding`).
  - Fields set the right `KeyboardOptions` (keyboard type, IME action), plus autofill hints where useful.
  - Check text selection, the context menu and autofill on iOS; they are where a non-native text field shows first.

## Accessibility
Covers TalkBack and VoiceOver, Switch Access and Switch Control, and large text.
- **Semantics carry over.** Compose semantics are mapped to Android accessibility nodes and to iOS accessibility elements. iOS support is younger: test every critical flow with VoiceOver early, not only at Phase 5.
- **Labels.** Every icon-only control has a `contentDescription` from string resources. Decorative images use `null`.
- **Touch targets** are at least 48×48 dp, which also meets Apple's 44×44 pt minimum. Material 3 components already comply; check custom ones.
- **Contrast** is at least 4.5:1 for text, and 3:1 for large text and UI controls. Never use color alone to convey meaning. iOS users can turn on Increase Contrast; decide in the design system whether the app follows it.
- **Text size.** Text uses `sp`. Layouts survive the largest font scale on Android (200%) and the largest text size on iOS without clipping, so text containers never get fixed heights. Check on iOS that the shared UI follows the system text size setting.
- **Structure.**
  - Group related content with `Modifier.semantics(mergeDescendants = true)`.
  - Mark headings with `semantics { heading() }`.
  - Keep the focus order logical.
- **Announcements.** Announce important changes such as errors through live regions or snackbars, never through animation alone. Respect "remove animations" on Android and Reduce Motion on iOS.

## Text and localisation
- **Strings.** All user-facing text lives in `composeResources/values/strings.xml`, with `values-<language>` folders for translations.
  - Plurals use `pluralStringResource`.
  - Use placeholders (`%1$s`), never string concatenation.
  - Outside a Composable (e.g. a notification built in common code), use the suspend `getString(Res.string.…)`.
- **Formats.** Format dates, numbers and currency for the user's locale. kotlinx-datetime formats are not locale-aware, so locale-sensitive formatting goes through a small `expect` function or interface backed by the platform formatters. Store times in UTC and display them in local time.
- **RTL.** Use `start`/`end`, never `left`/`right`. Test in an RTL language on both platforms (Android: the `ar-XB` pseudo-locale; iOS: the right-to-left pseudolanguage in the Xcode scheme).
- **Per-app language.**
  - Android 13+: set up `localeConfig` when the app supports several languages.
  - iOS: list the supported languages in `CFBundleLocalizations` in `Info.plist`. Compose resources are not `.lproj` folders, so without this list iOS shows the app in its development language only.
- **Copy** is short and specific: say what happened and what the user can do. Example: "No connection. Showing saved notes."

## Feedback and forms
- **Confirmations.** Confirm actions with a snackbar. For a reversible destructive action, offer Undo instead of a confirmation dialog.
- **Validation.** Validate a field when the user leaves it, and show the error under the field. Disable the submit button only when a visible reason explains why.
- **Long actions.** Show progress on the button and prevent double submits.
- **Motion and haptics** are subtle, purposeful and consistent. Haptic feedback goes through `LocalHapticFeedback`, so each platform plays its native feel.

## Previews
- **Coverage.** Every public Composable has previews for:
  - each `UiState`, through a `PreviewParameterProvider`;
  - light and dark (`AppTheme(darkTheme = true)`);
  - a large font scale;
  - for screens, a wide window.
- Android-only multipreviews (`@PreviewLightDark`, `@PreviewFontScale`, `@PreviewScreenSizes`) work in `androidMain` only. In `commonMain`, write the variants as separate `@Preview` functions.
- Previews double as screenshot tests (see [testing.md](testing.md#screenshot-tests)).
- A preview renders the Android look. Check iOS on a simulator before the PR, especially text fields, scrolling and insets.

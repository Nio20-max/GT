# 3) Detailed App Plan (UI Close To APK) With Concrete Code Examples

Chosen target for examples: Native Android (Kotlin + XML)

## UI principles to preserve from APK
- Landscape-first primary experience.
- Persistent global shell:
  - left module menu
  - top title bar
  - bottom economy/action bar
- Data-dense management screens.
- Contextual no-data helper panels with clear CTA.
- Tactical drag-and-drop lineup on football field.
- Visual language: dark green, yellow highlights, white bold text.

## App information architecture
- `MainActivity` hosts:
  - `MainShellFragment` (persistent frame + HUD)
  - feature fragments loaded into content container
- Feature fragments:
  - Club
  - Finances
  - Stadium
  - Squad
  - Lineup
  - Training
  - Scouting
  - Transfer Market
  - League
  - Ladder
  - Friends
  - Live
  - Chat
  - Shop
    - Champions League
    - Cups
    - Alliances
    - Tasks
    - Premium

## Runtime UX rules (locked)
- League match lock banner appears at 17:00 UTC and stays until 18:00 UTC kickoff.
- Cup/UCL lock banner appears at 12:00 UTC and stays until 13:00 UTC kickoff.
- If user edits lineup after lock, app shows "queued for next match" state.
- Friendly tile auto-displays cancelled status on cup/UCL conflict days.
- Training gain summary refreshes after 00:00 UTC tick.
- Daily training/finance mail badge refreshes at 08:00 Europe/London.

## Goal Tactics parity checklist in UI
- Club: my club, sponsors, ingame emails, accomplishments.
- Finances: money history and stars history grids.
- Stadium: unlimited seat extension with star scaling and building effects.
- Squad: sell, skill cards, upgrades, injuries up to 12 days.
- Lineup: next 3 matches, expanded formations, lock/queue behavior.
- Training: team/individual/tactics/training camps with repeat pricing logic.
- Scouting: money scout, stars scout, speedup, youth outcomes.
- Transfer market: filters, favorites, own sales, seasonal injections.
- League: fixtures/table/top scorers.
- Champions League and cups: dedicated competition screens.
- Ladder: on-demand result and improved rewards.
- Friends: custom series and cross-platform info parity.
- Chat: global + private + paid groups + alliance chat.
- Shop: simulated grants, ad events, premium tiers, perks, skill-card bundles.

## Core shell XML (APK-inspired)
```xml
<!-- res/layout/fragment_main_shell.xml -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/mainContainer"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/mainMenu"
        android:layout_width="240dp"
        android:layout_height="match_parent" />

    <RelativeLayout
        android:id="@+id/gameContainer"
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <ImageView
            android:id="@+id/backgroundImage"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:scaleType="centerCrop"
            android:src="@drawable/background_pitch" />

        <TextView
            android:id="@+id/topBar"
            android:layout_width="match_parent"
            android:layout_height="48dp"
            android:gravity="center"
            android:textStyle="bold"
            android:textColor="@color/gt_text" />

        <FrameLayout
            android:id="@+id/contentHost"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:layout_below="@id/topBar"
            android:layout_above="@id/bottomBar" />

        <LinearLayout
            android:id="@+id/bottomBar"
            android:layout_width="match_parent"
            android:layout_height="64dp"
            android:layout_alignParentBottom="true"
            android:orientation="horizontal">

            <ImageButton android:id="@+id/backButton" ... />
            <ImageButton android:id="@+id/menuButton" ... />

            <TextView android:id="@+id/starsValue" ... />
            <TextView android:id="@+id/moneyValue" ... />
            <TextView android:id="@+id/medipacksValue" ... />

            <ImageButton android:id="@+id/contextButton" ... />
        </LinearLayout>
    </RelativeLayout>
</FrameLayout>
```

## Example: Main shell binding in Kotlin
```kotlin
class MainShellFragment : Fragment(R.layout.fragment_main_shell) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val stars = view.findViewById<TextView>(R.id.starsValue)
        val money = view.findViewById<TextView>(R.id.moneyValue)
        val medipacks = view.findViewById<TextView>(R.id.medipacksValue)

        lifecycleScope.launch {
            viewModel.hudState.collect { hud ->
                stars.text = "⭐${hud.stars}"
                money.text = "€${hud.money}"
                medipacks.text = "💊${hud.medipacks}"
            }
        }

        view.findViewById<View>(R.id.starsValue).setOnClickListener {
            findNavController().navigate(R.id.action_global_shop)
        }
    }
}
```

## Example: Lineup screen (football field + draggable slots)
```xml
<!-- res/layout/fragment_lineup.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <ImageView
        android:id="@+id/fieldImage"
        android:layout_width="0dp"
        android:layout_height="0dp"
        android:src="@drawable/soccerfield"
        android:scaleType="fitXY"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toStartOf="@id/playersTable" />

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/playersTable"
        android:layout_width="250dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <FrameLayout android:id="@+id/slot1" ... />
    <FrameLayout android:id="@+id/slot2" ... />
    <FrameLayout android:id="@+id/slot3" ... />
</androidx.constraintlayout.widget.ConstraintLayout>
```

```kotlin
class LineupFragment : Fragment(R.layout.fragment_lineup) {
    private fun bindDragAndDrop(slot: View, playerCard: View) {
        playerCard.setOnLongClickListener {
            val shadow = View.DragShadowBuilder(it)
            it.startDragAndDrop(null, shadow, it.tag, 0)
            true
        }
        slot.setOnDragListener { _, event ->
            if (event.action == DragEvent.ACTION_DROP) {
                val playerId = event.localState as String
                viewModel.assignPlayerToSlot(playerId, slot.id)
                true
            } else false
        }
    }
}
```

## Example: No-data reusable component (APK-like)
```xml
<!-- res/layout/view_no_data_card.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:orientation="vertical">

    <ImageView android:id="@+id/characterImage" ... />
    <TextView android:id="@+id/message" ... />
    <Button android:id="@+id/actionPrimary" ... />
    <Button android:id="@+id/actionSecondary" ... />
</LinearLayout>
```

## Design tokens (match APK tone)
- `gt_bg_dark = #1D2B03`
- `gt_accent = #AFD50C`
- `gt_text = #FFFFFF`
- `gt_highlight = #FFFF00`
- `gt_row_even = #641D2B03`
- `gt_row_odd = #6492CC46`

## Interaction details to mirror
- All economy-changing actions require confirmation popups.
- Keep bottom bar always visible except full-screen overlays.
- Keep tab headers as horizontal segmented controls.
- Keep stat tables with alternating row shades.

## Performance and maintainability
- Use RecyclerView/ListAdapter + DiffUtil for all large tables.
- Use pagination for market and chat histories.
- Cache read-heavy data (league table snapshots, player cards).
- Use offline read cache with stale indicators.

## Feature parity checkpoints
1. Core shell + login + club + finances
2. Squad + lineup + training
3. Scouting + transfer market
4. League + live + ladder
5. Friends + chat + shop
6. Polish pass: animation, haptics, latency masking

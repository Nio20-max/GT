# 1) Decompiled APK Overview And UI/Layout Analysis

Source analyzed:
- `plan/Goal Tactics - Football MMO_1.2.4_APKPure_src/`
- `plan/Goal Tactics.md`

## High-Level APK Structure
- `AndroidManifest.xml`
  - Package: `com.xyrality.goaltactics`
  - Main launcher activity: `crc645877ad3d44b9b81b.MainActivity`
  - Orientation: `sensorLandscape` (landscape-first UX)
- `res/`
  - Full Android resource tree with a large set of custom game layouts
  - Rich localization (`values-*` for many languages)
- `lib/`
  - Native libraries for `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`
- `unknown/assemblies/`
  - Xamarin/Mono assembly manifest confirms C#/.NET stack
- `assets/`
  - Includes `roboto_bold.ttf` and Helpshift support data

## Technology Fingerprint
The APK is not a pure Java/Kotlin app. It is a Xamarin.Android app (C# compiled to Mono runtime):
- `libxamarin-app.so`, `libmonodroid.so`, `libmonosgen-2.0.so`
- `unknown/assemblies/assemblies.manifest` includes:
  - `GT.Droid`, `GT.Core`
  - `Xamarin.AndroidX.*`
  - `Microsoft.AspNetCore.SignalR.Client*`
  - `Plugin.InAppBilling`, `SkiaSharp`, `Microcharts`

Implication:
- Legacy client likely used C# domain models and custom native-backed UI controls.
- UI XML references many custom views under obfuscated Xamarin namespace `crc645877ad3d44b9b81b.*`.

## UI Architecture Findings

### 1. Screen shell and navigation layout
`mainlayout.xml` shows the global shell:
- Left side menu (`GTListView`) for module navigation
- Top bar title
- Bottom bar with resources and action buttons
- Main content frame (`@id/mainFrame`) where feature screens swap
- Floating chat/help buttons
- Overlay blockers/loading views

Concrete snippet:
```xml
<FrameLayout android:id="@id/mainContainer" ...>
    <crc645877ad3d44b9b81b.GTListView
        android:id="@id/mainMenu"
        android:layout_width="@dimen/mainlayout_main_menu_width"
        android:layout_height="fill_parent" />

    <RelativeLayout android:id="@id/gameContainer" ...>
        <TextView android:id="@id/topBar" .../>
        <FrameLayout android:id="@id/bottomBar" ...>
            <ImageButton android:id="@id/backButton" .../>
            <ImageButton android:id="@id/menuButton" .../>
            ...
            <ImageButton android:id="@id/contextMenuButton" .../>
        </FrameLayout>
        <FrameLayout android:id="@id/mainFrame" .../>
    </RelativeLayout>
</FrameLayout>
```

### 2. Resource HUD design
Bottom bar integrates medipacks, stars, and money counters with clickable star/medipack purchase triggers:
```xml
<LinearLayout android:id="@id/StarsButton" style="@style/ClickableResourcesStyle">
    <ImageView android:id="@id/resourcesStarsPlus" .../>
    <ImageView android:src="@drawable/balance_star" .../>
    <crc645877ad3d44b9b81b.AnimatedTextView android:id="@id/resourcesStars" .../>
</LinearLayout>
```

This confirms a always-visible economy HUD pattern, useful for retention and conversion loops.

### 3. Login and onboarding screen pattern
`login.xml` is split horizontally into:
- Facebook connect panel
- Username/password login panel
- Bottom row action buttons (`Support`, `QuickStart`, `NewPlayer`)

Concrete snippet:
```xml
<com.facebook.login.widget.LoginButton android:id="@id/registerFacebook" .../>
<crc645877ad3d44b9b81b.TextField android:id="@id/loginName" .../>
<crc645877ad3d44b9b81b.TextField android:id="@id/loginPassword" .../>
<Button android:id="@id/loginButton" android:text="@string/Login" .../>
```

### 4. Data-first module screens
Many modules use table/collection views + empty-state helper cards:
- `shop.xml`:
```xml
<crc645877ad3d44b9b81b.GTCollectionView android:id="@id/shop_OffersView" .../>
<crc645877ad3d44b9b81b.NoDataView android:id="@id/shop_NoOffersContainer"
    app:character="Anna" app:message="@string/NoOffersDescription"/>
```
- `transfermarkettable.xml` and `squad.xml` follow same pattern with contextual no-data CTAs.

### 5. Tactical lineup screen complexity
`lineupformation.xml` is one of the most important UI layouts:
- ConstraintLayout football field background
- 11 active player drop slots + bench drop slots
- Side player table
- Tactic/system combo boxes
- Strength and lock labels
- Dragging overlay view

Concrete snippet:
```xml
<crc645877ad3d44b9b81b.DropView android:id="@id/LineupFormationPosition_1" .../>
...
<crc645877ad3d44b9b81b.DropView android:id="@id/LineupFormationPosition_11" .../>
<crc645877ad3d44b9b81b.ComboBox android:id="@id/LineupFormation_SelectTactic" .../>
<crc645877ad3d44b9b81b.ComboBox android:id="@id/LineupFormation_SelectSystem" .../>
<crc645877ad3d44b9b81b.DraggableView android:id="@id/LineupFormation_PlayerDrag" .../>
```

### 6. Styling and visual language
From `res/values/styles.xml` and `res/values/colors.xml`:
- Theme: `GTTheme` (AppCompat NoActionBar, fullscreen, custom splash)
- Typographic base: bold `TextStyle` with shadow, Roboto font
- Button strategy: selector-driven green primary / gray inactive
- Palette: dark green football manager tone with yellow highlight and white text

Concrete snippets:
```xml
<style name="GTTheme" parent="@style/Theme.AppCompat.NoActionBar">
    <item name="android:windowBackground">@drawable/splash_screen</item>
    <item name="android:windowFullscreen">true</item>
    <item name="colorAccent">@color/colorAccentGreen</item>
</style>

<style name="TextStyle" parent="@android:style/Widget.TextView">
    <item name="android:textSize">12.0dip</item>
    <item name="android:textStyle">bold</item>
    <item name="android:textColor">@color/colorText</item>
    <item name="android:fontFamily">@font/roboto</item>
</style>
```

And key colors:
- `colorAccentGreen = #ffafd50c`
- `colorBackground = #ff1d2b03`
- `colorSection = #a0afd50c`
- `colorHighlight = #ffffff00`

### 7. Feature coverage visible from resources
Layout names and strings confirm full management loop:
- Club, sponsors, finances, stadium, squad, lineup, training
- Scouting and transfer market
- League + ladder + live match views
- Friends and chat
- Shop/in-app purchase and ads hooks

### 8. Third-party integrations visible in package
- Facebook Login
- Firebase messaging/analytics
- IronSource ad SDK
- Helpshift support
- Google Billing

## Practical Reverse-Engineering Constraints
- The workspace includes resources, manifest, dex, and Mono assemblies manifest, but no directly readable C# source code.
- Computation logic (e.g., exact formulas) is not directly visible in this apktool output.
- UI and information architecture are strongly recoverable and are sufficient to design a feature-faithful remake.

## Rebuild Guidance Extracted From APK
- Preserve landscape-first shell and persistent economy HUD.
- Keep the no-data helper cards with character hints (important for UX clarity).
- Keep tactical lineup drag-and-drop as a first-class interaction.
- Keep module framing: table/list heavy management surfaces + contextual action popups.
- Keep visual identity: dark-green football operations dashboard style.

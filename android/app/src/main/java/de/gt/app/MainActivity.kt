package de.gt.app

import android.media.MediaPlayer
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.ListView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import de.gt.app.data.ApiClient
import de.gt.app.data.ApiResult
import de.gt.app.data.ClubInfo
import de.gt.app.data.Profile
import de.gt.app.data.SessionStore
import de.gt.app.ui.MainMenuAdapter
import de.gt.app.ui.MenuEntry
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

class MainActivity : AppCompatActivity() {
    private lateinit var apiClient: ApiClient
    private lateinit var sessionStore: SessionStore
    private lateinit var mainFrame: FrameLayout
    private lateinit var topBar: TextView
    private lateinit var resourcesMoney: TextView
    private lateinit var resourcesStars: TextView
    private lateinit var resourcesMedipacks: TextView
    private lateinit var mainMenu: ListView
    private lateinit var menuAdapter: MainMenuAdapter
    private lateinit var menuBlocker: View
    private lateinit var loadingImage: ImageView
    private lateinit var backButton: ImageButton
    private lateinit var menuButton: ImageButton
    private lateinit var contextMenuButton: ImageButton
    private lateinit var gameContainer: View
    private lateinit var chatButton: ImageButton

    private var currentClub: ClubInfo? = null
    private var menuVisible = true
    private val navigationStack = mutableListOf<String>()

    private val menuItems = listOf(
        MenuEntry(section = "Club", title = "Club Info"),
        MenuEntry(title = "Squad"),
        MenuEntry(title = "Lineup"),
        MenuEntry(title = "Stadium"),
        MenuEntry(section = "Game", title = "League"),
        MenuEntry(title = "Challenges"),
        MenuEntry(title = "Ladder"),
        MenuEntry(section = "Economy", title = "Training"),
        MenuEntry(title = "Transfer Market"),
        MenuEntry(title = "Scouting"),
        MenuEntry(title = "Finance"),
        MenuEntry(title = "Sponsors"),
        MenuEntry(section = "Social", title = "Chat"),
        MenuEntry(title = "Friends"),
        MenuEntry(title = "Mail"),
        MenuEntry(section = "Other", title = "Accomplishments"),
        MenuEntry(title = "Statistics"),
        MenuEntry(title = "Shop"),
        MenuEntry(title = "Settings"),
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.mainlayout)

        apiClient = ApiClient(BuildConfig.GT_API_BASE)
        sessionStore = SessionStore(this)

        bindViews()
        initMainMenu()
        initBottomBar()
        initChatButton()

        updateResources(5_000_000, 20_000, 0)

        if (sessionStore.getToken().isNullOrBlank()) {
            showLogin()
        } else {
            hideLoadingScreen()
            showClubInfo()
            refreshClubData()
        }
    }

    private fun bindViews() {
        mainFrame = findViewById(R.id.mainFrame)
        topBar = findViewById(R.id.topBar)
        resourcesMoney = findViewById(R.id.resourcesMoney)
        resourcesStars = findViewById(R.id.resourcesStars)
        resourcesMedipacks = findViewById(R.id.resourcesMedipacks)
        mainMenu = findViewById(R.id.mainMenu)
        menuBlocker = findViewById(R.id.menuBlocker)
        loadingImage = findViewById(R.id.loadingImage)
        backButton = findViewById(R.id.backButton)
        menuButton = findViewById(R.id.menuButton)
        contextMenuButton = findViewById(R.id.contextMenuButton)
        gameContainer = findViewById(R.id.gameContainer)
        chatButton = findViewById(R.id.mainLayoutChatButton)
    }

    private fun initMainMenu() {
        menuAdapter = MainMenuAdapter(this, menuItems)
        mainMenu.adapter = menuAdapter
        mainMenu.setOnItemClickListener { _, _, position, _ ->
            if (sessionStore.getToken().isNullOrBlank()) {
                showLogin()
                return@setOnItemClickListener
            }
            playClick()
            menuAdapter.setSelected(position)
            navigateToSection(menuItems[position].title)
        }
        menuBlocker.visibility = View.GONE
    }

    private fun initBottomBar() {
        backButton.setOnClickListener {
            playClick()
            onBack()
        }
        menuButton.setOnClickListener {
            playClick()
            toggleMenu()
        }
        contextMenuButton.setOnClickListener {
            playClick()
        }

        findViewById<View>(R.id.MediPacksButton).setOnClickListener {
            navigateToSection("Shop")
        }
        findViewById<View>(R.id.StarsButton).setOnClickListener {
            navigateToSection("Shop")
        }
    }

    private fun initChatButton() {
        chatButton.setOnClickListener {
            playClick()
            navigateToSection("Chat")
        }
    }

    private fun hideLoadingScreen() {
        loadingImage.visibility = View.GONE
    }

    // --- Navigation ---

    private fun navigateToSection(section: String) {
        navigationStack.add(section)
        topBar.text = section

        when (section) {
            "Club Info" -> showClubInfo()
            "Squad" -> showLayout(R.layout.squad, section)
            "Lineup" -> showLayout(R.layout.lineupformation, section)
            "Stadium" -> showLayout(R.layout.stadiumlayout, section)
            "League" -> showLayout(R.layout.gamecourseliveview, section)
            "Challenges" -> showLayout(R.layout.challenges, section)
            "Ladder" -> showLayout(R.layout.ladderpopup, section)
            "Training" -> showLayout(R.layout.individualtrainingview, section)
            "Transfer Market" -> showLayout(R.layout.transfermarkettable, section)
            "Scouting" -> showLayout(R.layout.scoutingview, section)
            "Finance" -> showLayout(R.layout.financetab, section)
            "Sponsors" -> showLayout(R.layout.sponsorsview, section)
            "Chat" -> showLayout(R.layout.chatview, section)
            "Friends" -> showLayout(R.layout.friends, section)
            "Mail" -> showLayout(R.layout.mailstable, section)
            "Accomplishments" -> showLayout(R.layout.accomplishmentsview, section)
            "Statistics" -> showLayout(R.layout.statisticslayout, section)
            "Shop" -> showLayout(R.layout.shop, section)
            "Settings" -> showLayout(R.layout.mainsettings, section)
            "Live" -> showLayout(R.layout.liveview, section)
            else -> showClubInfo()
        }
    }

    private fun showLayout(layoutRes: Int, title: String) {
        topBar.text = title
        val content = LayoutInflater.from(this).inflate(layoutRes, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)
    }

    private fun onBack() {
        if (navigationStack.size > 1) {
            navigationStack.removeLast()
            val prev = navigationStack.last()
            navigationStack.removeLast()
            navigateToSection(prev)
        }
    }

    private fun toggleMenu() {
        menuVisible = !menuVisible
        mainMenu.visibility = if (menuVisible) View.VISIBLE else View.GONE
    }

    // --- Auth screens ---

    private fun showLogin() {
        topBar.text = getString(R.string.Login)
        hideLoadingScreen()
        val content = LayoutInflater.from(this).inflate(R.layout.login, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        val loginName = content.findViewById<EditText>(R.id.loginName)
        val loginPassword = content.findViewById<EditText>(R.id.loginPassword)
        val loginButton = content.findViewById<Button>(R.id.loginButton)
        val quickStartButton = content.findViewById<Button>(R.id.registerQuickStart)
        val newPlayerButton = content.findViewById<Button>(R.id.registerNewPlayer)
        val facebookButton = content.findViewById<Button>(R.id.registerFacebook)

        // Facebook login not supported in remake - hide
        facebookButton.text = getString(R.string.app_name)
        facebookButton.isEnabled = false

        loginButton.setOnClickListener {
            playClick()
            val username = loginName.text?.toString().orEmpty().trim()
            val password = loginPassword.text?.toString().orEmpty()
            if (username.length < 3 || password.length < 8) {
                Toast.makeText(this, "Username >= 3, Password >= 8 required", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            lifecycleScope.launch {
                loginButton.isEnabled = false
                when (val result = apiClient.login(username, password)) {
                    is ApiResult.Success -> {
                        sessionStore.saveToken(result.data)
                        showClubInfo()
                        refreshClubData()
                    }
                    is ApiResult.Failure -> {
                        Toast.makeText(this@MainActivity, result.message, Toast.LENGTH_SHORT).show()
                        loginButton.isEnabled = true
                    }
                }
            }
        }

        quickStartButton.setOnClickListener {
            playClick()
            showQuickRegister()
        }

        newPlayerButton.setOnClickListener {
            playClick()
            showRegisterNewPlayer()
        }
    }

    private fun showQuickRegister() {
        topBar.text = getString(R.string.QuickStart)
        val content = LayoutInflater.from(this).inflate(R.layout.quickregister, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        val teamName = content.findViewById<EditText>(R.id.quickEnterTeamName)
        val startButton = content.findViewById<Button>(R.id.quickStart)
        val signUpButton = content.findViewById<Button>(R.id.quickSignUp)

        startButton.setOnClickListener {
            playClick()
            val name = teamName.text?.toString().orEmpty().trim()
            if (name.length < 3) {
                Toast.makeText(this, "Team name must be at least 3 characters", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            // Quick registrations use team name as username with generated email/password
            lifecycleScope.launch {
                startButton.isEnabled = false
                val genPassword = "Quick${System.currentTimeMillis()}"
                val genEmail = "${name.lowercase().replace(" ", "")}@quick.gt"
                when (val regResult = apiClient.register(name, genEmail, genPassword)) {
                    is ApiResult.Success -> {
                        when (val loginResult = apiClient.login(name, genPassword)) {
                            is ApiResult.Success -> {
                                sessionStore.saveToken(loginResult.data)
                                showClubInfo()
                                refreshClubData()
                            }
                            is ApiResult.Failure -> {
                                Toast.makeText(this@MainActivity, loginResult.message, Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                    is ApiResult.Failure -> {
                        Toast.makeText(this@MainActivity, regResult.message, Toast.LENGTH_SHORT).show()
                    }
                }
                startButton.isEnabled = true
            }
        }

        signUpButton.setOnClickListener {
            playClick()
            showRegisterNewPlayer()
        }
    }

    private fun showRegisterNewPlayer() {
        topBar.text = getString(R.string.NewPlayer)
        val content = LayoutInflater.from(this).inflate(R.layout.registeruser, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        val username = content.findViewById<EditText>(R.id.registerName)
        val email = content.findViewById<EditText>(R.id.registerEmail)
        val password = content.findViewById<EditText>(R.id.registerPassword)
        val registerButton = content.findViewById<Button>(R.id.registerNextButton)
        val cancelButton = content.findViewById<Button>(R.id.registerCancelButton)

        registerButton.text = getString(R.string.Next)

        cancelButton.text = getString(R.string.Cancel)
        cancelButton.setOnClickListener {
            playClick()
            showLogin()
        }

        registerButton.setOnClickListener {
            playClick()
            val user = username.text?.toString().orEmpty().trim()
            val mail = email.text?.toString().orEmpty().trim()
            val pass = password.text?.toString().orEmpty()
            if (user.length < 3 || pass.length < 8 || !mail.contains("@")) {
                Toast.makeText(this, "Username>=3, valid email, password>=8 required", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            lifecycleScope.launch {
                registerButton.isEnabled = false
                when (val result = apiClient.register(user, mail, pass)) {
                    is ApiResult.Success -> {
                        Toast.makeText(this@MainActivity, "Account created! Logging in...", Toast.LENGTH_SHORT).show()
                        when (val loginResult = apiClient.login(user, pass)) {
                            is ApiResult.Success -> {
                                sessionStore.saveToken(loginResult.data)
                                showClubInfo()
                                refreshClubData()
                            }
                            is ApiResult.Failure -> {
                                Toast.makeText(this@MainActivity, loginResult.message, Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                    is ApiResult.Failure -> {
                        Toast.makeText(this@MainActivity, result.message, Toast.LENGTH_SHORT).show()
                    }
                }
                registerButton.isEnabled = true
            }
        }
    }

    // --- Game Screens ---

    private fun showClubInfo() {
        topBar.text = getString(R.string.Club)
        val content = LayoutInflater.from(this).inflate(R.layout.clubinfonew, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        // Populate if we have club data
        currentClub?.let { bindClubInfo(content, it) }
    }

    private fun bindClubInfo(view: View, club: ClubInfo) {
        view.findViewById<TextView>(R.id.clubInfoName)?.text = club.clubName
        updateResources(club.money, club.stars, club.medipacks)
    }

    // --- Data refresh ---

    private fun refreshClubData() {
        val token = sessionStore.getToken() ?: return
        lifecycleScope.launch {
            when (val result = apiClient.profile(token)) {
                is ApiResult.Success -> { /* profile valid */ }
                is ApiResult.Failure -> {
                    sessionStore.clear()
                    showLogin()
                    return@launch
                }
            }
            when (val clubResult = apiClient.getClub(token)) {
                is ApiResult.Success -> {
                    currentClub = clubResult.data
                    updateResources(clubResult.data.money, clubResult.data.stars, clubResult.data.medipacks)
                }
                is ApiResult.Failure -> { /* use defaults */ }
            }
        }
    }

    private fun updateResources(money: Long, stars: Int, medipacks: Int) {
        val nf = NumberFormat.getNumberInstance(Locale.US)
        resourcesMoney.text = nf.format(money)
        resourcesStars.text = nf.format(stars)
        resourcesMedipacks.text = nf.format(medipacks)
    }

    // --- Audio ---

    private fun playClick() {
        try {
            val mp = MediaPlayer.create(this, R.raw.click1)
            mp?.setOnCompletionListener { it.release() }
            mp?.start()
        } catch (_: Exception) { }
    }

    @Deprecated("Use onBack()")
    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (navigationStack.size > 1) {
            onBack()
        } else if (!sessionStore.getToken().isNullOrBlank()) {
            showClubInfo()
        } else {
            super.onBackPressed()
        }
    }
}

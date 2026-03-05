package de.gt.app

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ListView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import de.gt.app.data.ApiClient
import de.gt.app.data.ApiResult
import de.gt.app.data.Profile
import de.gt.app.data.SessionStore
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private lateinit var apiClient: ApiClient
    private lateinit var sessionStore: SessionStore
    private lateinit var mainFrame: FrameLayout
    private lateinit var topBar: TextView
    private lateinit var resourcesMoney: TextView
    private lateinit var resourcesStars: TextView
    private lateinit var resourcesMedipacks: TextView

    private val sections = listOf(
        "Dashboard",
        "Club",
        "Squad",
        "Lineup",
        "Training",
        "Market",
        "League",
        "Runtime",
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.gt_mainlayout_shell)

        apiClient = ApiClient(BuildConfig.GT_API_BASE)
        sessionStore = SessionStore(this)

        mainFrame = findViewById(R.id.mainFrame)
        topBar = findViewById(R.id.topBar)
        resourcesMoney = findViewById(R.id.resourcesMoney)
        resourcesStars = findViewById(R.id.resourcesStars)
        resourcesMedipacks = findViewById(R.id.resourcesMedipacks)

        resourcesMoney.text = "5,000,000"
        resourcesStars.text = "20,000"
        resourcesMedipacks.text = "0"

        initMainMenu()
        if (sessionStore.getToken().isNullOrBlank()) {
            renderAuth()
        } else {
            renderDashboardAndRefresh()
        }
    }

    private fun initMainMenu() {
        val menu = findViewById<ListView>(R.id.mainMenu)
        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, sections)
        menu.adapter = adapter
        menu.setOnItemClickListener { _, _, position, _ ->
            if (sessionStore.getToken().isNullOrBlank()) {
                renderAuth("Please login first")
                return@setOnItemClickListener
            }

            val selected = sections[position]
            if (selected == "Dashboard") {
                renderDashboardAndRefresh()
            } else {
                renderSection(selected)
            }
        }
    }

    private fun renderAuth(statusMessage: String = "") {
        topBar.text = "Account"
        val content = LayoutInflater.from(this).inflate(R.layout.view_auth, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        val inputUsername = content.findViewById<EditText>(R.id.inputUsername)
        val inputEmail = content.findViewById<EditText>(R.id.inputEmail)
        val inputPassword = content.findViewById<EditText>(R.id.inputPassword)
        val buttonLogin = content.findViewById<Button>(R.id.buttonLogin)
        val buttonRegister = content.findViewById<Button>(R.id.buttonRegister)
        val authProgress = content.findViewById<ProgressBar>(R.id.authProgress)
        val authStatus = content.findViewById<TextView>(R.id.authStatus)

        authStatus.text = statusMessage

        fun setLoading(loading: Boolean) {
            authProgress.visibility = if (loading) View.VISIBLE else View.GONE
            buttonLogin.isEnabled = !loading
            buttonRegister.isEnabled = !loading
        }

        buttonRegister.setOnClickListener {
            val username = inputUsername.text?.toString().orEmpty().trim()
            val email = inputEmail.text?.toString().orEmpty().trim()
            val password = inputPassword.text?.toString().orEmpty()
            if (!validateAuthInput(username, email, password, requireEmail = true)) {
                authStatus.text = "Username>=3, valid email, password>=8"
                return@setOnClickListener
            }

            lifecycleScope.launch {
                setLoading(true)
                when (val result = apiClient.register(username, email, password)) {
                    is ApiResult.Success -> {
                        authStatus.text = "Registration successful. Please login."
                    }

                    is ApiResult.Failure -> {
                        authStatus.text = result.message
                    }
                }
                setLoading(false)
            }
        }

        buttonLogin.setOnClickListener {
            val username = inputUsername.text?.toString().orEmpty().trim()
            val password = inputPassword.text?.toString().orEmpty()
            if (!validateAuthInput(username, email = "x@y.z", password = password, requireEmail = false)) {
                authStatus.text = "Username>=3 and password>=8 required"
                return@setOnClickListener
            }

            lifecycleScope.launch {
                setLoading(true)
                when (val result = apiClient.login(username, password)) {
                    is ApiResult.Success -> {
                        sessionStore.saveToken(result.data)
                        renderDashboardAndRefresh()
                    }

                    is ApiResult.Failure -> {
                        authStatus.text = result.message
                        setLoading(false)
                    }
                }
            }
        }
    }

    private fun renderDashboardAndRefresh() {
        topBar.text = "Dashboard"
        val content = LayoutInflater.from(this).inflate(R.layout.view_dashboard, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        val greeting = content.findViewById<TextView>(R.id.dashboardGreeting)
        val email = content.findViewById<TextView>(R.id.dashboardEmail)
        val status = content.findViewById<TextView>(R.id.dashboardStatus)
        val refreshButton = content.findViewById<Button>(R.id.buttonRefreshProfile)
        val logoutButton = content.findViewById<Button>(R.id.buttonLogout)

        refreshButton.setOnClickListener {
            refreshProfile(greeting, email, status)
        }

        logoutButton.setOnClickListener {
            sessionStore.clear()
            Toast.makeText(this, "Logged out", Toast.LENGTH_SHORT).show()
            renderAuth()
        }

        refreshProfile(greeting, email, status)
    }

    private fun renderSection(sectionName: String) {
        topBar.text = sectionName
        val content = LayoutInflater.from(this).inflate(R.layout.view_section, mainFrame, false)
        mainFrame.removeAllViews()
        mainFrame.addView(content)

        content.findViewById<TextView>(R.id.sectionTitle).text = sectionName
        content.findViewById<TextView>(R.id.sectionDescription).text =
            "$sectionName is wired and ready for deeper game features on top of the live backend contract."
    }

    private fun refreshProfile(greeting: TextView, email: TextView, status: TextView) {
        val token = sessionStore.getToken()
        if (token.isNullOrBlank()) {
            renderAuth("Session not found")
            return
        }

        status.text = "Refreshing profile..."
        lifecycleScope.launch {
            when (val profileResult = apiClient.profile(token)) {
                is ApiResult.Success -> {
                    bindProfile(profileResult.data, greeting, email)
                    status.text = "Connected to ${BuildConfig.GT_API_BASE}"
                }

                is ApiResult.Failure -> {
                    sessionStore.clear()
                    renderAuth(profileResult.message)
                }
            }
        }
    }

    private fun bindProfile(profile: Profile, greeting: TextView, email: TextView) {
        greeting.text = "Welcome, ${profile.username}"
        email.text = profile.email
    }

    private fun validateAuthInput(
        username: String,
        email: String,
        password: String,
        requireEmail: Boolean,
    ): Boolean {
        if (username.length < 3 || password.length < 8) return false
        if (!requireEmail) return true
        return email.contains("@") && email.contains(".")
    }
}

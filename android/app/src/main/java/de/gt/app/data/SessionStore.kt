package de.gt.app.data

import android.content.Context

class SessionStore(context: Context) {
    private val prefs = context.getSharedPreferences("gt_session", Context.MODE_PRIVATE)

    fun getToken(): String? = prefs.getString(KEY_TOKEN, null)

    fun saveToken(token: String) {
        prefs.edit().putString(KEY_TOKEN, token).apply()
    }

    fun clear() {
        prefs.edit().remove(KEY_TOKEN).apply()
    }

    companion object {
        private const val KEY_TOKEN = "token"
    }
}

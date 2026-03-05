package de.gt.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

class ApiClient(private val baseUrl: String) {
    suspend fun register(username: String, email: String, password: String): ApiResult<Unit> =
        withContext(Dispatchers.IO) {
            val body = JSONObject()
                .put("username", username)
                .put("email", email)
                .put("password", password)
                .toString()
            val response = request("POST", "/api/v1/auth/register", body = body)
            if (response.code in 200..299) {
                ApiResult.Success(Unit)
            } else {
                ApiResult.Failure(parseError(response.body, "Registration failed"))
            }
        }

    suspend fun login(username: String, password: String): ApiResult<String> = withContext(Dispatchers.IO) {
        val body = JSONObject()
            .put("username", username)
            .put("password", password)
            .toString()
        val response = request("POST", "/api/v1/auth/login", body = body)
        if (response.code !in 200..299) {
            return@withContext ApiResult.Failure(parseError(response.body, "Login failed"))
        }

        return@withContext try {
            val payload = JSONObject(response.body)
            val token = payload.getJSONObject("data").getString("token")
            ApiResult.Success(token)
        } catch (_: Exception) {
            ApiResult.Failure("Unexpected login response")
        }
    }

    suspend fun profile(token: String): ApiResult<Profile> = withContext(Dispatchers.IO) {
        val response = request(
            method = "GET",
            path = "/api/v1/me/profile",
            bearerToken = token,
        )
        if (response.code !in 200..299) {
            return@withContext ApiResult.Failure(parseError(response.body, "Profile request failed"))
        }

        return@withContext try {
            val payload = JSONObject(response.body).getJSONObject("data")
            if (!payload.optBoolean("authenticated")) {
                ApiResult.Failure("Session expired")
            } else {
                val user = payload.getJSONObject("user")
                ApiResult.Success(
                    Profile(
                        userId = user.optString("id"),
                        username = user.optString("username"),
                        email = user.optString("email"),
                    )
                )
            }
        } catch (_: Exception) {
            ApiResult.Failure("Unexpected profile response")
        }
    }

    private fun request(
        method: String,
        path: String,
        body: String? = null,
        bearerToken: String? = null,
    ): HttpResult {
        val url = URL(baseUrl.trimEnd('/') + path)
        val connection = (url.openConnection() as HttpURLConnection)
        connection.requestMethod = method
        connection.connectTimeout = 10000
        connection.readTimeout = 10000
        connection.setRequestProperty("Accept", "application/json")

        if (body != null) {
            connection.doOutput = true
            connection.setRequestProperty("Content-Type", "application/json")
        }

        if (!bearerToken.isNullOrBlank()) {
            connection.setRequestProperty("Authorization", "Bearer $bearerToken")
        }

        if (body != null) {
            OutputStreamWriter(connection.outputStream).use { it.write(body) }
        }

        val code = connection.responseCode
        val stream = if (code in 200..399) connection.inputStream else connection.errorStream
        val payload = stream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
        connection.disconnect()
        return HttpResult(code, payload)
    }

    private fun parseError(rawBody: String, fallback: String): String {
        return try {
            val parsed = JSONObject(rawBody)
            if (parsed.optBoolean("ok", true)) {
                fallback
            } else {
                parsed.optJSONObject("error")?.optString("message", fallback) ?: fallback
            }
        } catch (_: Exception) {
            fallback
        }
    }
}

data class Profile(
    val userId: String,
    val username: String,
    val email: String,
)

data class HttpResult(
    val code: Int,
    val body: String,
)

sealed interface ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>
    data class Failure(val message: String) : ApiResult<Nothing>
}

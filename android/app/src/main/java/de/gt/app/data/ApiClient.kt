package de.gt.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import org.json.JSONArray
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

    suspend fun getClub(token: String): ApiResult<ClubInfo> = withContext(Dispatchers.IO) {
        val response = request("GET", "/api/v1/club", bearerToken = token)
        if (response.code !in 200..299)
            return@withContext ApiResult.Failure(parseError(response.body, "Club request failed"))
        try {
            val d = JSONObject(response.body).getJSONObject("data")
            ApiResult.Success(ClubInfo(
                clubName = d.optString("club_name", "My Club"),
                leagueName = d.optString("league_name", "League"),
                rank = d.optInt("rank", 0),
                money = d.optLong("money", 5000000),
                stars = d.optInt("stars", 20000),
                medipacks = d.optInt("medipacks", 0),
                stadiumLevel = d.optInt("stadium_level", 1),
                fanCount = d.optInt("fan_count", 0),
            ))
        } catch (_: Exception) { ApiResult.Failure("Parse error") }
    }

    suspend fun getSquad(token: String): ApiResult<SquadData> = withContext(Dispatchers.IO) {
        val response = request("GET", "/api/v1/squad", bearerToken = token)
        if (response.code !in 200..299)
            return@withContext ApiResult.Failure(parseError(response.body, "Squad request failed"))
        try {
            val d = JSONObject(response.body).getJSONObject("data")
            val arr = d.optJSONArray("players") ?: JSONArray()
            val players = (0 until arr.length()).map { i ->
                val p = arr.getJSONObject(i)
                Player(
                    id = p.optString("id"), name = p.optString("name"),
                    position = p.optString("position"), age = p.optInt("age"),
                    strength = p.optDouble("strength", 0.0).toFloat(),
                    defence = p.optInt("defence"), shots = p.optInt("shots"),
                    playmaking = p.optInt("playmaking"), speed = p.optInt("speed"),
                    duel = p.optInt("duel"), stamina = p.optInt("stamina", 100),
                    morale = p.optInt("morale", 100), jerseyNumber = p.optInt("jersey_number", i + 1),
                    contractUntil = p.optString("contract_until", ""),
                )
            }
            ApiResult.Success(SquadData(players, d.optInt("formation_id", 0)))
        } catch (_: Exception) { ApiResult.Failure("Parse error") }
    }

    suspend fun getMatches(token: String): ApiResult<List<MatchInfo>> = withContext(Dispatchers.IO) {
        val response = request("GET", "/api/v1/matches", bearerToken = token)
        if (response.code !in 200..299)
            return@withContext ApiResult.Failure(parseError(response.body, "Matches request failed"))
        try {
            val arr = JSONObject(response.body).optJSONArray("data") ?: JSONArray()
            val matches = (0 until arr.length()).map { i ->
                val m = arr.getJSONObject(i)
                MatchInfo(
                    id = m.optString("id"), homeTeam = m.optString("home_team"),
                    awayTeam = m.optString("away_team"),
                    homeScore = if (m.has("home_score")) m.optInt("home_score") else null,
                    awayScore = if (m.has("away_score")) m.optInt("away_score") else null,
                    status = m.optString("status"), kickoff = m.optString("kickoff"),
                )
            }
            ApiResult.Success(matches)
        } catch (_: Exception) { ApiResult.Failure("Parse error") }
    }

    suspend fun getLeague(token: String): ApiResult<List<LeagueStanding>> = withContext(Dispatchers.IO) {
        val response = request("GET", "/api/v1/league", bearerToken = token)
        if (response.code !in 200..299)
            return@withContext ApiResult.Failure(parseError(response.body, "League request failed"))
        try {
            val arr = JSONObject(response.body).optJSONArray("data") ?: JSONArray()
            val standings = (0 until arr.length()).map { i ->
                val s = arr.getJSONObject(i)
                LeagueStanding(
                    rank = s.optInt("rank"), clubName = s.optString("club_name"),
                    played = s.optInt("played"), won = s.optInt("won"),
                    drawn = s.optInt("drawn"), lost = s.optInt("lost"),
                    goalsFor = s.optInt("goals_for"), goalsAgainst = s.optInt("goals_against"),
                    points = s.optInt("points"),
                )
            }
            ApiResult.Success(standings)
        } catch (_: Exception) { ApiResult.Failure("Parse error") }
    }

    suspend fun startTraining(token: String, playerId: String, skill: String): ApiResult<Unit> =
        withContext(Dispatchers.IO) {
            val body = JSONObject().put("player_id", playerId).put("skill", skill).toString()
            val response = request("POST", "/api/v1/training/start", body = body, bearerToken = token)
            if (response.code in 200..299) ApiResult.Success(Unit)
            else ApiResult.Failure(parseError(response.body, "Training start failed"))
        }

    suspend fun genericGet(token: String, path: String): ApiResult<JSONObject> =
        withContext(Dispatchers.IO) {
            val response = request("GET", path, bearerToken = token)
            if (response.code !in 200..299)
                return@withContext ApiResult.Failure(parseError(response.body, "Request failed"))
            try { ApiResult.Success(JSONObject(response.body)) }
            catch (_: Exception) { ApiResult.Failure("Parse error") }
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

private data class HttpResult(
    val code: Int,
    val body: String,
)

sealed interface ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>
    data class Failure(val message: String) : ApiResult<Nothing>
}

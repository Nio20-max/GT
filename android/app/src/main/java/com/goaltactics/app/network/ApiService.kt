package com.goaltactics.app.network

import com.goaltactics.app.model.Club
import com.goaltactics.app.model.Player
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {

    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): Club

    @GET("club")
    suspend fun getClub(): Club

    @GET("squad")
    suspend fun getSquad(): List<Player>
}

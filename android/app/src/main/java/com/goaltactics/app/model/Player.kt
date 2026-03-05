package com.goaltactics.app.model

data class Player(
    val id: Long = 0,
    val name: String = "",
    val age: Int = 0,
    val position: String = "",
    val overall: Int = 0,
    val stamina: Int = 100,
    val ballControl: Int = 0,
    val tackling: Int = 0,
    val passing: Int = 0,
    val shooting: Int = 0,
    val heading: Int = 0,
    val speed: Int = 0,
    val goalkeeping: Int = 0,
    val injured: Boolean = false,
    val booked: Boolean = false
)

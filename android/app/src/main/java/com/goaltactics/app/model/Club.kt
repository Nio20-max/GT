package com.goaltactics.app.model

data class Club(
    val id: Long = 0,
    val name: String = "",
    val managerName: String = "",
    val leagueLevel: Int = 1,
    val leaguePosition: Int = 0,
    val stadiumCapacity: Int = 0,
    val money: Int = 0,
    val stars: Int = 0,
    val medipacks: Int = 0,
    val players: List<Player> = emptyList()
)

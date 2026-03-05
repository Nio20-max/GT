package de.gt.app.data

data class Profile(
    val userId: String,
    val username: String,
    val email: String,
)

data class ClubInfo(
    val clubName: String,
    val leagueName: String,
    val rank: Int,
    val money: Long,
    val stars: Int,
    val medipacks: Int,
    val stadiumLevel: Int,
    val fanCount: Int,
)

data class Player(
    val id: String,
    val name: String,
    val position: String,
    val age: Int,
    val strength: Float,
    val defence: Int,
    val shots: Int,
    val playmaking: Int,
    val speed: Int,
    val duel: Int,
    val stamina: Int,
    val morale: Int,
    val jerseyNumber: Int,
    val contractUntil: String,
)

data class SquadData(
    val players: List<Player>,
    val formationId: Int,
)

data class MatchInfo(
    val id: String,
    val homeTeam: String,
    val awayTeam: String,
    val homeScore: Int?,
    val awayScore: Int?,
    val status: String,
    val kickoff: String,
)

data class LeagueStanding(
    val rank: Int,
    val clubName: String,
    val played: Int,
    val won: Int,
    val drawn: Int,
    val lost: Int,
    val goalsFor: Int,
    val goalsAgainst: Int,
    val points: Int,
)

data class TrainingSlot(
    val playerId: String,
    val playerName: String,
    val skill: String,
    val endsAt: String,
)

data class StadiumBuilding(
    val id: String,
    val name: String,
    val level: Int,
    val maxLevel: Int,
    val upgrading: Boolean,
)

data class TransferListing(
    val id: String,
    val playerName: String,
    val position: String,
    val strength: Float,
    val age: Int,
    val price: Long,
)

data class FinanceEntry(
    val date: String,
    val description: String,
    val amount: Long,
)

data class SponsorOffer(
    val id: String,
    val name: String,
    val amount: Long,
    val duration: Int,
)

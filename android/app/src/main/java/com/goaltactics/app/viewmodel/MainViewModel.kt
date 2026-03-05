package com.goaltactics.app.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.goaltactics.app.model.Club
import com.goaltactics.app.model.HudState

class MainViewModel : ViewModel() {

    private val _hudState = MutableLiveData(HudState())
    val hudState: LiveData<HudState> = _hudState

    private val _club = MutableLiveData<Club>()
    val club: LiveData<Club> = _club

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    fun updateHud(medipacks: Int, stars: Int, money: Int) {
        _hudState.value = HudState(medipacks, stars, money)
    }

    fun setClub(club: Club) {
        _club.value = club
        updateHud(club.medipacks, club.stars, club.money)
    }
}

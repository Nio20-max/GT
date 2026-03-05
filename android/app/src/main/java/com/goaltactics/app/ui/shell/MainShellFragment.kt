package com.goaltactics.app.ui.shell

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.goaltactics.app.R
import com.goaltactics.app.databinding.FragmentMainShellBinding
import com.goaltactics.app.viewmodel.MainViewModel

class MainShellFragment : Fragment() {

    private var _binding: FragmentMainShellBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MainViewModel by activityViewModels()
    private lateinit var menuAdapter: MainMenuAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMainShellBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupMenu()
        observeHud()
    }

    private fun setupMenu() {
        menuAdapter = MainMenuAdapter(buildMenuItems()) { item ->
            navigateToSection(item.destinationId)
        }
        binding.mainMenu.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = menuAdapter
        }
    }

    private fun buildMenuItems(): List<MainMenuAdapter.MenuItem> = listOf(
        // Team
        MainMenuAdapter.MenuItem(getString(R.string.menu_club), R.string.menu_section_team, R.id.action_shell_to_club),
        MainMenuAdapter.MenuItem(getString(R.string.menu_finances), null, R.id.action_shell_to_finances),
        MainMenuAdapter.MenuItem(getString(R.string.menu_stadium), null, R.id.action_shell_to_stadium),
        MainMenuAdapter.MenuItem(getString(R.string.menu_squad), null, R.id.action_shell_to_squad),
        MainMenuAdapter.MenuItem(getString(R.string.menu_lineup), null, R.id.action_shell_to_lineup),
        MainMenuAdapter.MenuItem(getString(R.string.menu_training), null, R.id.action_shell_to_training),
        MainMenuAdapter.MenuItem(getString(R.string.menu_scouting), null, R.id.action_shell_to_scouting),
        MainMenuAdapter.MenuItem(getString(R.string.menu_transfer_market), null, R.id.action_shell_to_transfer),
        // Competitions
        MainMenuAdapter.MenuItem(getString(R.string.menu_league), R.string.menu_section_competitions, R.id.action_shell_to_league),
        MainMenuAdapter.MenuItem(getString(R.string.menu_gt_ladder), null, R.id.action_shell_to_ladder),
        // Social
        MainMenuAdapter.MenuItem(getString(R.string.menu_friends), R.string.menu_section_social, R.id.action_shell_to_friends),
        MainMenuAdapter.MenuItem(getString(R.string.menu_live), null, R.id.action_shell_to_live),
        MainMenuAdapter.MenuItem(getString(R.string.menu_chat), null, R.id.action_shell_to_chat),
        // Other
        MainMenuAdapter.MenuItem(getString(R.string.menu_shop), R.string.menu_section_other, R.id.action_shell_to_shop),
    )

    private fun navigateToSection(actionId: Int) {
        findNavController().navigate(actionId)
    }

    private fun observeHud() {
        val bottomBar = binding.bottomBarContainer
        viewModel.hudState.observe(viewLifecycleOwner) { hud ->
            bottomBar.findViewById<android.widget.TextView>(R.id.resourcesMedipacks)?.text =
                hud.medipacks.toString()
            bottomBar.findViewById<android.widget.TextView>(R.id.resourcesStars)?.text =
                hud.stars.toString()
            bottomBar.findViewById<android.widget.TextView>(R.id.resourcesMoney)?.text =
                hud.money.toString()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

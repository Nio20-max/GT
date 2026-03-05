package com.goaltactics.app.ui.login

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.goaltactics.app.R
import com.goaltactics.app.databinding.FragmentLoginBinding

class LoginFragment : Fragment() {

    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnLogin.setOnClickListener {
            val username = binding.loginName.text.toString().trim()
            val password = binding.loginPassword.text.toString().trim()
            if (username.isNotEmpty() && password.isNotEmpty()) {
                navigateToShell()
            }
        }

        binding.btnQuickStart.setOnClickListener { navigateToShell() }
    }

    private fun navigateToShell() {
        findNavController().navigate(R.id.action_login_to_shell)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

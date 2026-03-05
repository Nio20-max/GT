package com.goaltactics.app.ui.shell

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import androidx.annotation.StringRes
import androidx.recyclerview.widget.RecyclerView
import com.goaltactics.app.R

class MainMenuAdapter(
    private val items: List<MenuItem>,
    private val onClick: (MenuItem) -> Unit
) : RecyclerView.Adapter<MainMenuAdapter.ViewHolder>() {

    data class MenuItem(
        val title: String,
        @StringRes val sectionHeaderRes: Int?,
        val destinationId: Int
    )

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val sectionTitle: TextView = view.findViewById(R.id.menuCellTitle)
        val cellButton: FrameLayout = view.findViewById(R.id.menuCellButton)
        val cellText: TextView = view.findViewById(R.id.menuCellText)
        val cellImage: ImageView = view.findViewById(R.id.menuCellImage)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_main_menu, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // Section header visibility
        if (item.sectionHeaderRes != null) {
            holder.sectionTitle.visibility = View.VISIBLE
            holder.sectionTitle.setText(item.sectionHeaderRes)
        } else {
            holder.sectionTitle.visibility = View.GONE
        }

        holder.cellText.text = item.title
        holder.cellButton.setOnClickListener { onClick(item) }
    }

    override fun getItemCount(): Int = items.size
}

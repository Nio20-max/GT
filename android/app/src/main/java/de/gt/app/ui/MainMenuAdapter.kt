package de.gt.app.ui

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import de.gt.app.R

data class MenuEntry(
    val section: String? = null,
    val title: String,
    val iconRes: Int = 0,
)

class MainMenuAdapter(
    private val context: Context,
    private val items: List<MenuEntry>,
) : BaseAdapter() {

    private var selectedPosition = -1

    fun setSelected(position: Int) {
        selectedPosition = position
        notifyDataSetChanged()
    }

    override fun getCount() = items.size
    override fun getItem(position: Int) = items[position]
    override fun getItemId(position: Int) = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.mainmenucell, parent, false)

        val entry = items[position]
        val sectionTitle = view.findViewById<TextView>(R.id.menuCellTitle)
        val button = view.findViewById<FrameLayout>(R.id.menuCellButton)
        val textView = view.findViewById<TextView>(R.id.menuCellText)
        val imageView = view.findViewById<ImageView>(R.id.menuCellImage)

        if (entry.section != null) {
            sectionTitle.visibility = View.VISIBLE
            sectionTitle.text = entry.section
        } else {
            sectionTitle.visibility = View.GONE
        }

        textView.text = entry.title
        if (entry.iconRes != 0) {
            imageView.setImageResource(entry.iconRes)
            imageView.visibility = View.VISIBLE
        } else {
            imageView.visibility = View.GONE
        }

        if (position == selectedPosition) {
            button.setBackgroundResource(R.drawable.menu_row_selected_selector)
        } else {
            button.setBackgroundResource(R.drawable.menu_row_selector)
        }

        return view
    }
}

package de.gt.app.views

import android.content.Context
import android.graphics.Canvas
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Shader
import android.util.AttributeSet
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.RelativeLayout
import android.widget.TextView

/** Draggable player view for lineup formation drag-and-drop */
class DraggableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr)

/** Drop target for lineup formation */
class DropView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr)

/** Star rating display for player strength */
class StrengthStarsView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {

    var stars: Float = 0f
        set(value) {
            field = value
            removeAllViews()
            val full = value.toInt()
            val half = if (value - full >= 0.5f) 1 else 0
            repeat(full) { addStar(1f) }
            if (half > 0) addStar(0.5f)
            repeat(5 - full - half) { addStar(0f) }
        }

    private fun addStar(fill: Float) {
        val iv = ImageView(context)
        val size = (16 * resources.displayMetrics.density).toInt()
        iv.layoutParams = LayoutParams(size, size)
        val resName = when {
            fill >= 1f -> "star_full"
            fill >= 0.5f -> "star_half"
            else -> "star_empty"
        }
        val resId = resources.getIdentifier(resName, "drawable", context.packageName)
        if (resId != 0) iv.setImageResource(resId)
        addView(iv)
    }
}

/** Gradient progress bar for stadium buildings */
class GradientProgressBar @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var progress: Float = 0f
        set(value) { field = value.coerceIn(0f, 1f); invalidate() }

    private val bgPaint = Paint().apply { color = 0xFF333333.toInt() }
    private val fgPaint = Paint()

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), bgPaint)
        if (progress > 0f) {
            fgPaint.shader = LinearGradient(
                0f, 0f, width * progress, 0f,
                0xFF00AA00.toInt(), 0xFF00FF00.toInt(),
                Shader.TileMode.CLAMP
            )
            canvas.drawRect(0f, 0f, width * progress, height.toFloat(), fgPaint)
        }
    }
}

/** Player model display (jersey + face) */
class PlayerModelView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    private val jerseyView = ImageView(context)
    private val faceView = ImageView(context)

    init {
        addView(jerseyView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
        addView(faceView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
    }

    fun setJersey(resId: Int) { jerseyView.setImageResource(resId) }
    fun setFace(resId: Int) { faceView.setImageResource(resId) }
}

/** Round avatar for player display */
class PlayerRoundAvatar @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr)

/** Player attribute specifications display */
class PlayerSpecifications @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    init { orientation = VERTICAL }
}

/** Side notification slide-in view */
class SideNotificationView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr)

/** Individual skill display */
class SkillView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr)

/** Skills container view */
class SkillsView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    init { orientation = VERTICAL }
}

/** Stadium building progress bar */
class StadiumProgressBar @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : ProgressBar(context, attrs, defStyleAttr)

/** Tab button in tab bar */
class TabButton @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : TextView(context, attrs, defStyleAttr) {

    var isActive: Boolean = false
        set(value) {
            field = value
            val bgRes = resources.getIdentifier(
                if (value) "tab_middle" else "tab_middle_inactive", "drawable", context.packageName
            )
            if (bgRes != 0) setBackgroundResource(bgRes)
        }
}

/** Tab header container */
class TabHeaderView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    init { orientation = HORIZONTAL }
}

/** Tabs container view */
class TabsView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr)

/** Tactics training progress bar */
class TacticsProgressBar @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : ProgressBar(context, attrs, defStyleAttr)

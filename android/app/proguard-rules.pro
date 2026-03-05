# Keep model classes and JSON field names used by org.json parsing.
-keep class de.gt.app.data.** { *; }

# Keep Kotlin metadata that can be used by runtime tooling.
-keep class kotlin.Metadata { *; }

# Keep lifecycle and coroutine internals that may be accessed reflectively.
-keep class androidx.lifecycle.** { *; }
-dontwarn kotlinx.coroutines.**

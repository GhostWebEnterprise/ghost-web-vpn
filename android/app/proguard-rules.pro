# Keep WireGuard GoBackend JNI surface intact
-keep class com.wireguard.android.backend.** { *; }
-keep class com.wireguard.config.** { *; }
-keep class com.wireguard.crypto.** { *; }
-keep class com.wireguard.util.** { *; }

# JSR-305 nullness annotations are compile-time only; the tunnel library's
# @NonNullForAll references them but they are not on the runtime classpath.
-dontwarn javax.annotation.**

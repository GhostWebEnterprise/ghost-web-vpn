import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Local (git-ignored) signing overrides: android/keystore.properties with
// storeFile / storePassword / keyAlias / keyPassword. CI instead injects
// ANDROID_KEYSTORE_* environment variables sourced from GitHub secrets.
val keystoreProps = Properties().apply {
    val propsFile = rootProject.file("keystore.properties")
    if (propsFile.exists()) propsFile.inputStream().use { load(it) }
}

fun signingValue(envVar: String, prop: String?): String? =
    System.getenv(envVar)?.takeIf { it.isNotBlank() } ?: prop

android {
    namespace = "cfd.ghostbin.ghostwebvpn"
    compileSdk = 35

    defaultConfig {
        applicationId = "cfd.ghostbin.ghostwebvpn"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "0.7.1"
    }

    signingConfigs {
        create("release") {
            val storeFilePath = signingValue("ANDROID_KEYSTORE_PATH", keystoreProps.getProperty("storeFile"))
            val storePass = signingValue("ANDROID_KEYSTORE_PASSWORD", keystoreProps.getProperty("storePassword"))
            val alias = signingValue("ANDROID_KEY_ALIAS", keystoreProps.getProperty("keyAlias"))
            val keyPass = signingValue("ANDROID_KEY_PASSWORD", keystoreProps.getProperty("keyPassword"))
                ?: storePass
            if (storeFilePath != null && storePass != null && alias != null) {
                storeFile = rootProject.file(storeFilePath)
                this.storePassword = storePass
                this.keyAlias = alias
                this.keyPassword = keyPass
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // Sign only when a keystore is actually configured, so CI builds
            // without signing secrets still produce an (unsigned) release APK.
            val releaseSigning = signingConfigs.getByName("release")
            if (releaseSigning.storeFile != null) {
                signingConfig = releaseSigning
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("com.wireguard.android:tunnel:1.0.20260102")
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.2")
}

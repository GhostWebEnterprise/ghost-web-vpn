export default [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "script",
      globals: {
        chrome: "readonly",
        PROXY_PRESETS: "readonly",
        LOCATION_PRESETS: "readonly",
        findPreset: "readonly",
        findProxyPreset: "readonly",
        GEONODE_PROXY_LIST_URL: "readonly"
      }
    },
    rules: {
      "no-undef": "error",
      "no-unused-vars": "warn",
      "no-empty": "warn",
      "no-useless-escape": "warn"
    }
  }
];

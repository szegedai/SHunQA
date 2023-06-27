// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  css: ["~/assets/css/main.css"],
  devtools: { enabled: true },
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  app: {
    head: {
      title: "Projectroom41: SHunQA",
    },
    // buildAssetsDir: "/demo_qa/_nuxt/",
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL || "https://chatbot-rgai3.inf.u-szeged.hu/demo_qa/api",
      // apiUrl: process.env.API_URL || "http://localhost:25565/api",
    }
  },
});

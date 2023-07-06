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
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL || "https://chatbot-rgai3.inf.u-szeged.hu/demo_qa/api",
      debug: process.env.DEBUG === 'true' || false,
      elasticTables: process.env.FRONTEND_ELASTIC_TABLES?.split(',') || [],
    }
  },
});

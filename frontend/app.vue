<template>
  <div class="container lg:max-w-2xl mt-7">
    <div class="flex flex-row items-center justify-between">
      <span class="flex flex-row space-x-1">
        <img class="w-8 h-8" src="@/assets/icon.svg" />
        <h1 class="text-3xl mb-2" v-html="$t('app.title')"></h1>
      </span>
      <div class="flex flex-row space-x-2">
        <select v-model="locale" class="rounded-md border border-gray-300 p-1 bg-white">
          <option value="hu">hu</option>
          <option value="en">en</option>
        </select>
      </div>
    </div>

    <ClientOnly>
      <SearchAndResults />
    </ClientOnly>
  </div>
</template>

<script setup>
const config = useRuntimeConfig().public;
const { locale } = useI18n()
</script>

<style>
body,
html,
#app {
  @apply bg-gray-50;
  padding: 0;
  margin: 0;
  width: 100%;
  min-height: 100%;
  height: 100%;
}
</style>
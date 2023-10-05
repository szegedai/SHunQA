<template>
    <div class="w-full mb-2 select-none border-l-4 p-4 font-medium" :class="`${colorVariants[color]}`">{{ text }}</div>
</template>

<script setup>
defineProps({
    text: String,
    color: String,
})

const colorVariants = {
    blue: 'hover:border-blue-500 border-blue-400 bg-blue-100',
    red: 'hover:border-red-500 border-red-400 bg-red-100',
    gray: 'hover:border-gray-500 border-gray-400 bg-gray-100',
    green: 'border-lime-600 bg-gray-200/80 italic',
  }
</script>
<template>
    <!-- <p>Téééégy feel egy kééérdééést.</p> -->
    <Vue3Lottie :animation-data="FAQJson" :height="400" :width="400" />
</template>

<script setup>
import FAQJson from '~/assets/animations/138566-frequently-asked-question-faq.json'
</script>

<!-- { "answers": [], "system": {} } -->
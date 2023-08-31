<template>
    <!-- <p>Kerestük közel, kerestük messze, azonban sajnos épp erre nem tudunk válaszolni.</p> -->
    <Vue3Lottie :animation-data="NoAnswerJson" :height="400" :width="400" />
</template>

<script setup>
import NoAnswerJson from '~/assets/animations/98448-no-task.json'
</script>

<!-- { "answers": [ { "answer": "", "elastic_score": 0, "end": 0, "lemmatized_context": "", "model_score": -1, "official_context": "", "official_question": "valami?", "relevant_context": "", "start": 0 } ], "system": { "id": "64a29495bdec28053a7b772b" } } -->
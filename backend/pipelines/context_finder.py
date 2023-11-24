from backend.exceptions.check_fail import CheckFailError
from backend.exceptions.pipeline_fail import PipelineFailError
from backend.pipelines.pipeline_steps import PipelineSteps


class ContextFinder(PipelineSteps):
    def __init__(self):
        pass

    def run(self, data: dict) -> dict | PipelineFailError:
        # ({h1}\n{h2}\n{h3}\n{context}\n)*context_num (-\n)
        # answer=data["reader"]["answer"],
        # context=data["context"],
        # text_start=data["reader"]["start"],
        # text_end=data["reader"]["end"],
        # data["official_contexts"]

        # kiszámolni a contextek határát
        # megkeresni, hogy ez melyik contextben van
        # megtartani azt a contextet, elshiftelni a kijelölt választ
        # levágni az elejéről a metát (ha lehetséges), elshiftelni a választ

        context_lengths = [len(context) for context in data["official_contexts"]]
        context_starts = [sum(context_lengths[:i]) for i in range(len(context_lengths))]
        context_ends = [
            sum(context_lengths[: i + 1]) for i in range(len(context_lengths))
        ]
        context_intervals = [
            (context_starts[i], context_ends[i]) for i in range(len(context_lengths))
        ]
        context_num = len(context_lengths)

        answer_start = data["reader"]["start"]
        answer_end = data["reader"]["end"]

        context_start = -1
        context_end = -1
        context_id = -1

        for i in range(context_num):
            if (
                context_intervals[i][0] <= answer_start < context_intervals[i][1]
                and context_intervals[i][0] <= answer_end < context_intervals[i][1]
            ):
                context_start = context_intervals[i][0]
                context_end = context_intervals[i][1]
                context_id = i
                break

        if context_start == -1 or context_end == -1:
            raise PipelineFailError("context_not_found", "Context not found", data)

        context = data["context"][context_start:context_end]
        answer_start -= context_start
        answer_end -= context_start

        # metadata = f"{data['h1'][context_id]}\n{data['h2'][context_id]}\n{data['h3'][context_id]}\n\n"
        metadata = ""
        metadata += (
            data["h1"][context_id] + "\n" if data["h1"][context_id] else ""
        )
        metadata += (
            data["h2"][context_id] + "\n" if data["h2"][context_id] else ""
        )
        metadata += (
            data["h3"][context_id] + "\n" if data["h3"][context_id] else ""
        )
        metadata += "\n"
        if answer_start > len(metadata):
            context = context[len(metadata) :]
            answer_start -= len(metadata)
            answer_end -= len(metadata)

        context_finder_data = {
            "extracted_context": context,
            "start": answer_start,
            "end": answer_end,
            "context_id": context_id,
        }
        data["context_finder"] = context_finder_data

        data["metadata"] = []
        data["metadata"].append(
            {
                "title": data["h1"][context_id] if data["h1"][context_id] else "",
                "section": data["h2"][context_id]
                if data["h2"][context_id]
                else "" + (" > " + data["h3"][context_id])
                if data["h3"][context_id]
                else "",
                "file_name": data["file_names"][context_id],
            }
        )

        return data

    def data_check(self, data: dict) -> dict | CheckFailError:
        """Check if the input data contains the required keys.

        Args:
            data (dict): A dictionary containing input data.

        Raises:
            CheckFailError: If the input data lacks 'context' or 'official_contexts' or 'reader' keys.

        Returns:
            dict | CheckFailError: A dictionary containing the input data.
        """
        if (
            "context" not in data.keys()
            or "official_contexts" not in data.keys()
            or "reader" not in data.keys()
        ):
            raise CheckFailError(
                "missing_context_or_official_contexts_or_reader",
                "Missing context or official contexts or reader in data",
                data,
            )
        return data

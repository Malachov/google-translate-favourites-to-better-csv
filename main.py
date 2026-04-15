import pandas as pd
from googletrans import Translator
import asyncio


async def main(
    input_csv_path: str = "input.csv",
    output_csv_path: str = "output.csv",
    input_src_identifier="čeština",
    translation_src_lang="en",
    max_synonyms=4,
    max_definitions=2,
    max_examples=2,
) -> None:
    translator = Translator()

    df = pd.read_csv(input_csv_path, header=None)

    # Ensure that the source language column is in the correct position
    df[df[0] == input_src_identifier] = df[df[0] == input_src_identifier].iloc[
        :, [1, 0, 3, 2]
    ]

    df = df.iloc[:, 2:]

    df.columns = [translation_src_lang, input_src_identifier]

    res = await translator.translate(
        df[translation_src_lang].tolist(),
        src=translation_src_lang,
        dest=translation_src_lang,
    )

    synonyms_global_list = []
    definitions_global_list = []
    examples_global_list = []

    for i in res:
        data = i.extra_data

        synonyms = []

        if data["synonyms"]:
            for s in data["synonyms"]:
                for inner_s in s[1][:max_synonyms]:
                    synonyms.append(inner_s[0][0])
        else:
            synonyms.append("")

        synonyms_global_list.append(", ".join(synonyms))

        definitions = []

        if data["definitions"]:
            for d in data["definitions"]:
                for inner_d in d[1][:max_definitions]:
                    definitions.append(f"{d[0]}: {inner_d[0]}")
        else:
            definitions.append("")

        definitions_global_list.append(" | ".join(definitions))

        examples = []

        if data["examples"]:
            for e in data["examples"]:
                for k in e[:max_examples]:
                    examples.append(k[0].replace("<b>", "").replace("</b>", ""))
        else:
            examples.append("")

        examples_global_list.append(" | ".join(examples))

    combined_definitions_examples = [
        " === ".join([definition, example])
        if definition and example
        else definition or example
        for definition, example in zip(definitions_global_list, examples_global_list)
    ]

    new_df = pd.concat(
        [
            df,
            pd.DataFrame(
                {
                    "synonyms": synonyms_global_list,
                    "definitions_examples": combined_definitions_examples,
                }
            ),
        ],
        axis=1,
    )

    new_df.to_csv(output_csv_path, index=False)


if __name__ == "__main__":
    asyncio.run(
        main(input_csv_path="input_example.csv", output_csv_path="output_example.csv")
    )
    # asyncio.run(main(input_csv_path="input.csv"))
    # asyncio.run(main(input_csv_path="input.csv", input_src_identifier="Czech"))

# Copyright Log10, Inc 2023


from omegaconf import DictConfig, open_dict, OmegaConf

import hydra
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import logging
import semver
from llmeval import __version__

# TODO: Define data class for prompt
# TODO: Define data class for tests


@hydra.main(version_base=None, config_path=".", config_name="llmeval")
def main(cfg: DictConfig) -> None:
    # TODO: Support non-openai models.
    llm = ChatOpenAI()

    if cfg.version is not None:
        config_version = semver.Version.parse(cfg.version)
        app_version = semver.Version.parse(__version__.__version__)
        logging.debug(f"config_version={config_version}")
        logging.debug(f"app_version={app_version}")

        if app_version > config_version:
            logging.warn(
                f"llmeval version {app_version} is newer than config version {config_version} and may not be compatible. Please update config files to match with llmeval version {app_version}."
            )
        elif app_version < config_version:
            logging.error(
                f"llmeval version {app_version} is older than config version {config_version} and may not be compatible. Please update llmeval cli."
            )
    else:
        logging.warn(
            "No version specified in report. Assuming using latest llmeval version"
        )

    for i in range(cfg.n_tries):
        # TODO: If messages is available, assume it is a chat model.
        messages = [(message.role, message.content) for message in cfg.prompts.messages]
        template = ChatPromptTemplate.from_messages(messages)

        metrics = cfg.prompts.tests.metrics
        variables = cfg.prompts.variables

        test_skipped = False
        if hasattr(cfg.prompts.tests, "skip"):
            test_skipped = cfg.prompts.tests.skip

        logging.debug(metrics)

        # Substitute variables in template with reference values.
        for reference in cfg.prompts.tests.references:
            # Verify reference has all expected variables.
            missing_variables = False
            for variable in variables:
                if variable.name not in reference.input:
                    logging.warn(
                        f"Variable {variable} is not in reference input. Skipping."
                    )
                    missing_variables = True
            if missing_variables:
                continue

            logging.debug(f"reference={reference}")
            messages = template.format_messages(**reference.input)
            logging.debug(f"messages={messages}")
            response = llm(messages)

            with open_dict(reference):
                reference["actual"] = response.content

                for metric_spec in metrics:
                    logging.debug(f"metric={metric_spec}")
                    locals = {"prompt": str(messages), "actual": response.content}

                    metric_skipped = False
                    if hasattr(metric_spec, "skip"):
                        metric_skipped = metric_spec.skip

                    if hasattr(reference, "expected"):
                        locals["expected"] = reference.expected

                    exec(metric_spec.code, None, locals)
                    metric_value = locals["metric"]
                    result = locals["result"]
                    logging.debug(f"result={result}")

                    logging.debug(f"metric.name={metric_spec.name}")
                    # Check whether value is already set.
                    if "metrics" not in reference:
                        reference["metrics"] = {}

                    # Determine whether to skip metric.
                    reference_skipped = False
                    if hasattr(reference, "skip"):
                        reference_skipped = reference.skip

                    reference["metrics"][metric_spec.name] = {
                        "metric": metric_value,
                        "result": "pass" if result else "fail",
                        "skipped": reference_skipped or metric_skipped or test_skipped,
                    }

        with open(f"report-{i}.yaml", "w") as f:
            f.write(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    main()

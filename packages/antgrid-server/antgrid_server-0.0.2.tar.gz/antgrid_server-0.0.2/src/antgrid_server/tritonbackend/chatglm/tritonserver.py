import argparse
import numpy as np
from pytriton.decorators import batch, first_value, group_by_values
from pytriton.model_config import DynamicBatcher, ModelConfig, Tensor
from pytriton.triton import Triton, TritonConfig
import logging

LOGGER = logging.getLogger("examples.huggingface_stable_diffusion.server")

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging in debug mode.",
    )
    return parser.parse_args()


def main():
    """Initialize server with model."""
    args = _parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s")

    log_verbose = 1 if args.verbose else 0
    config = TritonConfig(exit_on_error=True, log_verbose=log_verbose)

    with Triton(config=config) as triton:
        import antgrid_server.tritonbackend.chatglm.tritonmodel as tritonmodel
        model = tritonmodel.PytritonModel()
        triton.bind(
            model_name="ChatGLM_6B",
            infer_func= model._infer_fn,
            inputs=[
                Tensor(name="input", dtype=np.bytes_, shape=(1,)),
                Tensor(name="history", dtype=np.bytes_, shape=(1,)),
                Tensor(name="max_length", dtype=np.int64, shape=(1,)),
                Tensor(name="top_p", dtype=np.float32, shape=(1,)),
                Tensor(name="temperature", dtype=np.float32, shape=(1,)),
            ],
            outputs=[
                Tensor(name="response", dtype=np.bytes_, shape=(1,)),
                Tensor(name="history", dtype=np.bytes_, shape=(1,)),
            ],
            config=ModelConfig(
                max_batch_size=4,
                batcher=DynamicBatcher(
                    max_queue_delay_microseconds=100,
                ),
            ),
        )

        triton.bind(
            model_name="ChatGLM_6B_additer",
            infer_func= model._add_iter,
            inputs=[
                Tensor(name="input", dtype=np.bytes_, shape=(1,)),
                Tensor(name="history", dtype=np.bytes_, shape=(1,)),
                Tensor(name="max_length", dtype=np.int64, shape=(1,)),
                Tensor(name="top_p", dtype=np.float32, shape=(1,)),
                Tensor(name="temperature", dtype=np.float32, shape=(1,)),
                Tensor(name="tid", dtype=np.int64, shape=(1,)),
            ],
            outputs=[
                Tensor(name="response", dtype=np.bytes_, shape=(1,)),
                Tensor(name="history", dtype=np.bytes_, shape=(1,)),
            ],
            config=ModelConfig(
                max_batch_size=4,
                batcher=DynamicBatcher(
                    max_queue_delay_microseconds=100,
                ),
            ),
        )

        triton.bind(
            model_name="ChatGLM_6B_fn_iter",
            infer_func= model._infer_fn_iter,
            inputs=[
                Tensor(name="tid", dtype=np.int64, shape=(1,)),
            ],
            outputs=[
                Tensor(name="response", dtype=np.bytes_, shape=(1,)),
                Tensor(name="history", dtype=np.bytes_, shape=(1,)),
            ],
            config=ModelConfig(
                max_batch_size=4,
                batcher=DynamicBatcher(
                    max_queue_delay_microseconds=100,
                ),
            ),
        )
        
        triton.serve()


if __name__ == "__main__":
    main()
from antgrid_server.server.register import start as server_start

from antgrid_server.tritonbackend.baichuan.tritonserver import main as baichuan_start
from antgrid_server.tritonbackend.chatglm.tritonserver import main as chatglm_start
from antgrid_server.tritonbackend.llama2_7b_chat.tritonserver import main as llama2_start
from antgrid_server.tritonbackend.sd1_5.tritonserver import main as sd_start
# Copyright (C) 2022. Huawei Technologies Co., Ltd. All rights reserved. Redistribution and use in source and binary
# forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


""" 11th July 2022 """

EPFL_BEST_LUT = {
    'adder': {'corr. LUT': [185], 'corr. lvl': [119]},
    'bar': {'corr. LUT': [512], 'corr. lvl': [4]},
    'div': {'corr. LUT': [3248], 'corr. lvl': [1194]},
    'hyp': {'corr. LUT': [39826], 'corr. lvl': [4492]},
    'log2': {'corr. LUT': [6513], 'corr. lvl': [132]},
    'max': {'corr. LUT': [522], 'corr. lvl': [189]},
    'multiplier': {'corr. LUT': [4792], 'corr. lvl': [114]},
    'sin': {'corr. LUT': [1205], 'corr. lvl': [61]},
    'sqrt': {'corr. LUT': [3027], 'corr. lvl': [1096]},
    'square': {'corr. LUT': [3232], 'corr. lvl': [76]},
    'arbiter': {'corr. LUT': [304], 'corr. lvl': [80]},
    'ctrl': {'corr. LUT': [26], 'corr. lvl': [2]},
    'cavlc': {'corr. LUT': [68], 'corr. lvl': [3]},
    'dec': {'corr. LUT': [264], 'corr. lvl': [2]},
    'i2c': {'corr. LUT': [200], 'corr. lvl': [10]},
    'int2float': {'corr. LUT': [24], 'corr. lvl': [4]},
    'mem_ctrl': {'corr. LUT': [2019], 'corr. lvl': [21]},
    'priority': {'corr. LUT': [100], 'corr. lvl': [26]},
    'router': {'corr. LUT': [50], 'corr. lvl': [5]},
    'voter': {'corr. LUT': [1279], 'corr. lvl': [19]},
    'sixteen': {'corr. LUT': [3511769], 'corr. lvl': [32]},
    'twenty': {'corr. LUT': [4393495], 'corr. lvl': [33]},
    'twentythree': {'corr. LUT': [4908145], 'corr. lvl': [34]},
}

EPFL_BEST_LVL = {
    'adder': {'corr. LUT': [379], 'corr. lvl': [5]},
    'bar': {'corr. LUT': [512], 'corr. lvl': [4]},
    'div': {'corr. LUT': [29369], 'corr. lvl': [197]},
    'hyp': {'corr. LUT': [144809], 'corr. lvl': [501]},
    'log2': {'corr. LUT': [8894], 'corr. lvl': [52]},
    'max': {'corr. LUT': [811], 'corr. lvl': [10]},
    'multiplier': {'corr. LUT': [13670], 'corr. lvl': [25]},
    'sin': {'corr. LUT': [683103], 'corr. lvl': [10]},
    'sqrt': {'corr. LUT': [25876], 'corr. lvl': [192]},
    'square': {'corr. LUT': [4021], 'corr. lvl': [10]},
    'arbiter': {'corr. LUT': [1162], 'corr. lvl': [5]},
    'ctrl': {'corr. LUT': [26], 'corr. lvl': [2]},
    'cavlc': {'corr. LUT': [68], 'corr. lvl': [3]},
    'dec': {'corr. LUT': [264], 'corr. lvl': [2]},
    'i2c': {'corr. LUT': [221], 'corr. lvl': [3]},
    'int2float': {'corr. LUT': [27], 'corr. lvl': [3]},
    'mem_ctrl': {'corr. LUT': [2225], 'corr. lvl': [6]},
    'priority': {'corr. LUT': [132], 'corr. lvl': [4]},
    'router': {'corr. LUT': [56], 'corr. lvl': [3]},
    'voter': {'corr. LUT': [1386], 'corr. lvl': [12]},
    'sixteen': {'corr. LUT': [5396002], 'corr. lvl': [16]},
    'twenty': {'corr. LUT': [6928118], 'corr. lvl': [16]},
    'twentythree': {'corr. LUT': [7922493], 'corr. lvl': [17]},
}
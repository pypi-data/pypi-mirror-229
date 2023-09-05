"""

Copyright (c) 2023 Qualiteg Inc. all rights reserved.

This program is dual-licensed under the terms of the:
1) GNU Affero General Public License, version 3, or any later version.
2) A commercial license agreement provided by Qualiteg Inc.

If you choose to use or redistribute this program under the terms of AGPLv3:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

If you wish to use or redistribute this program under a commercial license:
Please contact Qualiteg Inc.(https://qualiteg.com/contact) directly to obtain the terms and pricing.

"""

from abc import ABC, abstractmethod


class TokenSamplerBase(ABC):
    def do_sample(self, logits, top_k=None, top_p=None, temperature=1.0, past_tokens=None, penalty=None,
                  penalty_method="multiplicative"):
        params = {
            "logits": logits,
            "top_k": top_k,
            "top_p": top_p,
            "temperature": temperature,
            "past_tokens": past_tokens,
            "penalty": penalty,
            "penalty_method": penalty_method
        }
        return self.process(logits, params)

    def process(self, logits, params):
        return self.get_sampler().process(logits, params)

    @abstractmethod
    def get_sampler(self):
        pass

import torch
import torch.nn as nn


class OpalNetBlock(nn.Module):
    def __init__(self, in_chn, out_chn):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_chn, out_chn),
            nn.ReLU(),
            nn.BatchNorm1d(out_chn),
        )

    def forward(self, x):
        return self.net(x)


class OpalNetModule(nn.Module):
    def __init__(self, n_uid, n_mid, emb_dim: int):
        super(OpalNetModule, self).__init__()

        self.u_emb = nn.Embedding(n_uid, emb_dim)
        self.m_emb = nn.Embedding(n_mid, emb_dim)

        # self.u_emb_mlp = nn.Embedding(n_uid, emb_dim)
        # self.m_emb_mlp = nn.Embedding(n_mid, emb_dim)

        self.bn_u_emb = nn.BatchNorm1d(emb_dim)
        self.bn_m_emb = nn.BatchNorm1d(emb_dim)
        # 
        # self.bn_u_emb_mlp = nn.BatchNorm1d(emb_dim)
        # self.bn_m_emb_mlp = nn.BatchNorm1d(emb_dim)

        self.mlp_bn = nn.BatchNorm1d(emb_dim * 2)
        self.mf_bn = nn.BatchNorm1d(emb_dim)
        self.fc = nn.Sequential(
            nn.Linear(emb_dim * 3, emb_dim * 3),
            nn.BatchNorm1d(emb_dim * 3),
            nn.SiLU(),
            nn.Linear(emb_dim * 3, 1),
        )

    def forward(self, uid, mid):
        """

        Notes:
            ┌───┐
            │UID├────┬───────────────────┐
            └───┘    │                   │
                 ┌───▼────┐ ┌────┐ ┌─────▼─────┐ ┌──────┐ ┌───────┐
                 │DOT PROD├─┤RELU├─►CONCATENATE├─►LINEAR├─►PREDICT│
                 └───▲────┘ └────┘ └─────▲─────┘ └──────┘ └───────┘
            ┌───┐    │                   │
            │MID├────┴───────────────────┘
            └───┘

        Args:
            uid:
            mid:

        Returns:

        """

        # Shape of Emb: [Batch Size, Embed Size]
        u_emb = self.u_emb(uid)[:, 0, :]
        m_emb = self.m_emb(mid)[:, 0, :]
        u_emb: torch.Tensor = self.bn_u_emb(u_emb)
        m_emb: torch.Tensor = self.bn_m_emb(m_emb)
        # u_emb_mlp = self.u_emb_mlp(uid)[:, 0, :]
        # m_emb_mlp = self.m_emb_mlp(mid)[:, 0, :]
        # u_emb_mlp: torch.Tensor = self.bn_u_emb_mlp(u_emb_mlp)
        # m_emb_mlp: torch.Tensor = self.bn_m_emb_mlp(m_emb_mlp)

        # [Batch Size, Embed Size * 2]
        x_mlp = self.mlp_bn(torch.concat([u_emb, m_emb], dim=1))

        # [Batch Size, 1]
        x_mf = self.mf_bn(u_emb * m_emb)

        # [Batch Size, Emb Size * 3]
        x = torch.concat((x_mlp, x_mf), dim=1)
        x = self.fc(x)
        return x

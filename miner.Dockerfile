FROM subnet:neuron

WORKDIR /app/

COPY --from=neuron-image /app/ ./

ENV PATH="/app/venv:$PATH"

ENTRYPOINT python \
    -m neurons.miner \
    --netuid $NETUID \
    --subtensor.network $NETWORK \
    --wallet.name $WALLET_NAME \
    --wallet.hotkey $WALLET_HOTKEY \

function biquadFilterEffect(type, frequency, Q, gain) {
    return (context, input) => {
        filter = context.createBiquadFilter();
        filter.type = type;
        filter.frequency.value = frequency;
        filter.Q.value = Q;
        filter.gain.value = gain;
        input.connect(filter);
        return filter;
    };
}
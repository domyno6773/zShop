FROM ghcr.io/wiiu-env/devkitppc:20260225

# Pinned WUPS toolchain from the official wiiu-env C++ example.
COPY --from=ghcr.io/wiiu-env/wiiupluginsystem:20260418 /artifacts $DEVKITPRO
WORKDIR /project

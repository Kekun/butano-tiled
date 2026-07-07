BNTMX_GRAPHICSFILES := $(foreach dir,	$(BUILD),	$(notdir $(wildcard $(dir)/*.bntmx.bmp)))

BNTMX_OFILES_GRAPHICS := $(BNTMX_GRAPHICSFILES:.bntmx.bmp=_bntmx_gfx.o)

OFILES += $(BNTMX_OFILES_GRAPHICS)

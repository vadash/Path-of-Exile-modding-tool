//PRECOMPILE ps_4_0 BloomGather
//PRECOMPILE ps_4_0 BloomGather DST_FP32 1
//PRECOMPILE ps_gnm BloomGather
//PRECOMPILE ps_gnm BloomGather DST_FP32 1
//PRECOMPILE ps_vkn BloomGather
//PRECOMPILE ps_vkn BloomGather DST_FP32 1

#ifdef DST_FP32
	#pragma PSSL_target_output_format (target 0 FMT_32_GR)
#endif

CBUFFER_BEGIN(cdepth_aware_blur) 
	int viewport_width;
	int viewport_height;
	int mips_count;
	float weight_mult;
	float4 frame_to_dynamic_scale;
CBUFFER_END

TEXTURE2D_DECL( src_sampler );

struct PInput
{
	float4 screen_coord : SV_POSITION;
	float2 tex_coord : TEXCOORD0;
};

float4 BloomGather( PInput input ) : PIXEL_RETURN_SEMANTIC
{
	return 0;
}

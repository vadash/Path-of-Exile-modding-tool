//PRECOMPILE ps_4_0 BloomCutoff
//PRECOMPILE ps_4_0 BloomCutoff DST_FP32 1
//PRECOMPILE ps_gnm BloomCutoff
//PRECOMPILE ps_gnm BloomCutoff DST_FP32 1
//PRECOMPILE ps_vkn BloomCutoff
//PRECOMPILE ps_vkn BloomCutoff DST_FP32 1

#ifdef DST_FP32
	#pragma PSSL_target_output_format (target 0 FMT_32_GR)
#endif

CBUFFER_BEGIN(cdepth_aware_blur) 
	int viewport_width;
	int viewport_height;
	float cutoff;
	float intensity;
	float4 frame_to_dynamic_scale;
CBUFFER_END

TEXTURE2D_DECL( src_sampler );

struct PInput
{
	float4 screen_coord : SV_POSITION;
	float2 tex_coord : TEXCOORD0;
};


float3 Luminance(float3 color)
{
	return 0;
}
float4 BloomCutoff( PInput input ) : PIXEL_RETURN_SEMANTIC
{
	return 0;
}

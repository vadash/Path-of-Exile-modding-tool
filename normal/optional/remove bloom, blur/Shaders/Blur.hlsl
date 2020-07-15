//PRECOMPILE ps_4_0 ApplyBlur
//PRECOMPILE ps_4_0 ApplyBlur DST_FP32 1
//PRECOMPILE ps_gnm ApplyBlur
//PRECOMPILE ps_gnm ApplyBlur DST_FP32 1
//PRECOMPILE ps_vkn ApplyBlur
//PRECOMPILE ps_vkn ApplyBlur DST_FP32 1

#ifdef DST_FP32
	#pragma PSSL_target_output_format (target 0 FMT_32_GR)
#endif

CBUFFER_BEGIN(cdepth_aware_blur) 
	int viewport_width;
	int viewport_height;
	float4 radii;
	float gamma;
	float exp_mult;
	int mip_level;
CBUFFER_END

TEXTURE2D_DECL( data_sampler );
TEXTURE2D_DECL( depth_sampler );
TEXTURE2D_DECL( normal_sampler );

struct PInput
{
	float4 screen_coord : SV_POSITION;
	float2 tex_coord : TEXCOORD0;
};

float4 ApplyBlur( PInput input ) : PIXEL_RETURN_SEMANTIC
{
	return 0;
}

//PRECOMPILE ps_4_0 BrightPassPS
//PRECOMPILE ps_gnm BrightPassPS
//PRECOMPILE ps_vkn BrightPassPS

CBUFFER_BEGIN( cbright_pass_desc )
	// bright pass constants
	float4 dynamic_resolution_scale;
	float4 downsample_offsets[ 2 ];
	float bloom_intensity = 0.3f;
	float bloom_cutoff = 0.3f;
CBUFFER_END

TEXTURE2D_DECL( source_sampler );

struct PInput
{
	float4 pos : SV_POSITION;
	float2 texture_uv : TEXCOORD0;
};

//Performs 4x4 downsample
float4 GetDownsampledPixel(float2 texture_uv)
{
	return 0;
}

float4 BrightPassPS( PInput input ) : PIXEL_RETURN_SEMANTIC
{
	return 0;
}

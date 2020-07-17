#define max_lights_count 0

CBUFFER_BEGIN(cscreenspace_gi) 
CBUFFER_END

struct PInput
{
};

float3 Project(in float3 world_point, in float4x4 proj_matrix)
{
}

float3 Unproject(in float2 screen_coord, in float nonlinear_depth, in float4x4 inv_proj_matrix)
{
}

float3 UnprojectLinear(in float2 screen_coord, in float linear_depth, in float4x4 inv_proj_matrix)
{
}

float2 GetPixelTexSize(in int mip_level, in int downscale)
{
}

float2 GetPixelScreenSize(in int mip_level, in int downscale)
{
}

float2 TexToScreenCoord(in float2 tex_coord, in float2 pixel_tex_size, in float2 pixel_screen_size)
{
}

float2 ScreenToTexCoord(in float2 screen_coord, in float2 pixel_tex_size, in float2 pixel_screen_size)
{
}

float2 ScreenToPixelCoord(in float2 screen_coord, in float2 pixel_screen_size)
{
}

float2 TexToPixelCoord(in float2 tex_coord, in float2 pixel_tex_size)
{
}

float2 PixelToTexCoord(in float2 pixel_coord, in float2 pixel_tex_size)
{
}

float2 PixelToScreenCoord(in float2 pixel_coord, in float2 pixel_screen_size)
{
}

float rand(float2 v){
}

struct Intersection
{
};


int GetLevelStartMult(int mip_level)
{
}

float4 GetChannelMask(float channel_index)
{
}

Intersection GetDepthIntersectionHierarchial(in float3 view_ray_start, float3 view_ray_end, float occlusion_dist_threshold)
{
}


struct OutPixel
{
};

void SwapFloat(inout float a, inout float b)
{
}
void SwapInt(inout int a, inout int b)
{
}
OutPixel ComputeScreenspaceShadows( PInput input )
{
}
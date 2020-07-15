//PRECOMPILE ps_4_0 PostProcessPS DETAIL_LEVEL 0
//PRECOMPILE ps_4_0 PostProcessPS DETAIL_LEVEL 1
//PRECOMPILE ps_gnm PostProcessPS DETAIL_LEVEL 0
//PRECOMPILE ps_gnm PostProcessPS DETAIL_LEVEL 1
//PRECOMPILE ps_vkn PostProcessPS DETAIL_LEVEL 0
//PRECOMPILE ps_vkn PostProcessPS DETAIL_LEVEL 1


CBUFFER_BEGIN( cpost_processing_desc )
	int target_width;
	int target_height;

	float4 src_frame_to_dynamic_scale;
	float4 target_frame_to_dynamic_scale;

	float4x4 viewproj_matrix;
	float4x4 inv_viewproj_matrix;

	float4 sphere_info; // xyz = position, w = radius
	float4 muddle_sampler_info;
	float breach_time;
	float time;
	
	float4 decay_map_minmax;
	float4 decay_map_size;
	float decay_map_time;
	float decay_map_type;
	float creation_time;
	float global_stability;
	float4 stabiliser_position;
	float post_transform_ratio;
	
	float original_intensity = 1;
	float exposure;
	float fade_amount;
	//float4 fade_color;
	bool fade_enable = false;
	float overlay_intensity;
	float4 blur_params;
	bool shimmer_enable = false;
	bool desaturation_enable = false;
	bool post_transform_enable = false;
	bool breach_enable = false;
	bool decay_enable = false;
CBUFFER_END

#include "Shaders/Include/Util.hlsl"
//#include "Shaders/Include/Lighting.hlsl"
//#include "Shaders/Include/ResourceOrb.hlsl"

TEXTURE2D_DECL( source_sampler );
TEXTURE2D_DECL( depth_sampler );

TEXTURE2D_DECL( bloom_sampler );
TEXTURE2D_DECL( shimmer_sampler );
TEXTURE2D_DECL( desaturation_sampler );
TEXTURE2D_DECL( crack_sdm_sampler );
TEXTURE2D_DECL( breach_edge_sampler );
TEXTURE2D_DECL( muddle_sampler );
TEXTURE2D_DECL( overlay_sampler );
TEXTURE2D_DECL( decay_map_sampler );
TEXTURE2D_DECL( stable_map_sampler );
TEXTURE2D_DECL( palette_sampler );
TEXTURE2D_DECL( space_tex_sampler );


TEXTURE3D_DECL( desaturation_transform_sampler );
TEXTURE3D_DECL( post_transform_sampler0 );
TEXTURE3D_DECL( post_transform_sampler1 );
TEXTURE3D_DECL( breach_transform_sampler );

struct PInput
{
	float4 screen_coord : SV_POSITION;
	float2 texture_uv : TEXCOORD0;
};

float3 Project(in float3 world_point, in float4x4 proj_matrix)
{
	float4 world_point4;
	world_point4.xyz = world_point;
	world_point4.w = 1.0f;
	float4 normalized_pos = mul(world_point4, proj_matrix);
	normalized_pos /= normalized_pos.w;
	float2 screen_point = normalized_pos.xy * 0.5f + float2(0.5f, 0.5f);
	screen_point.y = 1.0f - screen_point.y;
	return float3(screen_point.xy, normalized_pos.z);
}

float3 Unproject(in float2 screen_coord, in float nonlinear_depth, in float4x4 inv_proj_matrix)
{
	float4 projected_pos;
	projected_pos.x = screen_coord.x * 2.f - 1.f;
	projected_pos.y = ( 1.f - screen_coord.y ) * 2.f - 1.f;
	projected_pos.z = nonlinear_depth;
	projected_pos.w = 1.f;
	float4 world_pos = mul( projected_pos, inv_proj_matrix );
	world_pos /= world_pos.w;
	return world_pos.xyz;
}

float3 ApplyToneMapping(float3 linear_color, float exposure)
{
	return 1.0f - exp(-linear_color * exposure);
}


float SigmaFunc(float val)
{
	return 0.5f + sign(val - 0.5f) * pow(saturate(abs(val - 0.5f) * 2.0f), 10.0f) / 2.0f;
	//return atan((val - 0.2f) * 10.0f) / (3.1415f * 0.5f) * 0.5f + 0.5f;
}

float3 rgb2hsv(float3 c)
{
	float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));
	float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));

	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return float3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}
 

float3 hsv2rgb(float3 c)
{
	float4 K = float4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
	float3 p = abs(frac(c.xxx + K.xyz) * 6.0 - K.www);
	return c.z * lerp(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

float4 ApplyDesaturation(float4 color, float2 tex_coord)
{
	float4 desaturation_sample = SAMPLE_TEX2D( desaturation_sampler, SamplerLinearClamp, tex_coord );
	float4 desaturated_color = color;

	/*float3 hsv = rgb2hsv(color);
	float value = hsv.z;//dot(desaturated_color.rgb, float3(0.299, 0.587, 0.114));
	desaturated_color.rgb = float3(1.0f, 1.0f, 1.0f) * pow(SigmaFunc(value), 4.0f);*/

	desaturated_color.rgb = SAMPLE_TEX3DLOD( desaturation_transform_sampler, SamplerLinearClamp, float4( pow( saturate(color.rgb), 1.0 / 2.2 ), 0.f ) ).rgb;

	float ratio = saturate(desaturation_sample.r);// * (1.0f - pow(saturate(hsv.y), 3.0f));
	return lerp(color, desaturated_color, ratio);
}

float4 ApplyVignette(float4 color, float2 screen_coord)
{
	return color;
}


float4 ApplyOverlay(float4 color, float2 screen_coord)
{
	float4 overlay_sample = SAMPLE_TEX2D( overlay_sampler, SamplerLinearClamp, screen_coord );
	//overlay_sample.rgb *= overlay_sample.a; //for png's

	return lerp(color, overlay_sample, overlay_sample.a * overlay_intensity);
}

float rand(float2 v){
	return frac(sin(dot(v.xy, float2(12.9898, 78.233))) * 43758.5453);
}

float rand3(float3 v){
	return frac(sin(dot(v.xyz, float3(12.9898, 78.233, 164.2999))) * 43758.5453);
}

float4 GetRadialBlur(float2 screen_coord, float2 blur_intensity, float blur_curvature)
{
	return 0;
}

float GetGlobalDecayTime()
{
	//return fmod(time, 5.0f) * 1.0f + 28.0f;
	return decay_map_time;
}

struct DecayField
{
	float stability;
	float decay_time;
	float3 gradient;
	float curvature;
	float temp_mult;
	float glow_mult;
};

DecayField GetDecayField(float3 world_pos)
{
	float2 uv_pos = (world_pos.xy - decay_map_minmax.xy) / (decay_map_minmax.zw - decay_map_minmax.xy + 1e-5f);
	float4 decay_sample = SAMPLE_TEX2DLOD(decay_map_sampler, SamplerLinearWrap, float4(uv_pos, 0.0f, 0.0f));
	DecayField decay_field;
	float start_time = decay_sample.x;
	float decay_time = GetGlobalDecayTime() - start_time;
	float stability = SAMPLE_TEX2DLOD(stable_map_sampler, SamplerLinearWrap, float4(uv_pos, 0.0f, 0.0f)).x;

	float2 step_size = (decay_map_minmax.zw - decay_map_minmax.xy) / decay_map_size.xy;
	decay_field.gradient = float3(decay_sample.yz / step_size, 0.0f);

	decay_field.stability = stability;

	decay_field.temp_mult = 0.3f + 0.7f / (0.9f + 5.0f * length(decay_field.gradient));
	decay_field.temp_mult = lerp(decay_field.temp_mult, 0.5f, global_stability);
	{
		float stability_wave = (1.0f - (length(world_pos - stabiliser_position.xyz) - 300.0f - pow(max(0.0f, creation_time), 2.0f) * 1000.0f) * 0.0005f);
		//non-constant width
		//decay_time = max(decay_time, 50.0f - stability_wave * 50.0f);
		//constant width
		float transition_len = 1.0f / 70.0f;
		decay_time = max(decay_time / (length(decay_field.gradient) + 1e-4f) * transition_len + 1.0f, 50.0f - stability_wave * 50.0f);
		decay_field.gradient *= 1.0f / (length(decay_field.gradient) + 1e-4f) * transition_len;
	}
		
	decay_field.curvature = decay_sample.w / (step_size.x);

	decay_field.glow_mult = saturate(start_time + 8.0f);
	decay_field.decay_time = decay_time;
 
	return decay_field;
}


float3 BlackBody(float _t)
{
	// See: http://en.wikipedia.org/wiki/Planckian_locus
	//      under "Approximation"

	float u = (0.860117757 + 1.54118254e-4*_t + 1.28641212e-7*_t*_t)
			/ (1.0 + 8.42420235e-4*_t + 7.08145163e-7*_t*_t);

	float v = (0.317398726 + 4.22806245e-5*_t + 4.20481691e-8*_t*_t)
			/ (1.0 - 2.89741816e-5*_t + 1.61456053e-7*_t*_t);

	// http://en.wikipedia.org/wiki/CIE_1960_color_space
	// -> http://en.wikipedia.org/wiki/XYZ_color_space

	float x = 3.0 * u / (2.0 * u - 8.0 * v + 4.0);
	float y = 2.0 * v / (2.0 * u - 8.0 * v + 4.0);
	float z = 1.0 - x - y;

	float Y = 1.0;
	float X = (Y/y) * x;
	float Z = (Y/y) * z;

	// http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
	float3x3 XYZtosRGB = float3x3(
				3.2404542,-1.5371385,-0.4985314,
			-0.9692660, 1.8760108, 0.0415560,
				0.0556434,-0.2040259, 1.0572252
	);

	float3 RGB = mul(XYZtosRGB, float3(X,Y,Z));
	return pow(saturate(RGB * pow(0.0004*_t, 4.0)), 2.2f) * 2.0f;
}	



#define decay_length 200.0f
float GetDecayOffsetLen(DecayField decay_field)
{
	float acceleration = 40.5f / (1.0f + decay_field.curvature * 300.0f);

	float3 decay_grad = decay_field.gradient;
	float time_diff = max(0.0f, decay_field.decay_time);
	
	
	float a = dot(decay_grad, decay_grad);
	float b = 2.0f * time_diff * length(decay_grad) + 2.0f / acceleration;
	float c = time_diff * time_diff;
	
	float d = b * b - 4.0f * a * c;
	//return min(500.0f, -(-b + sqrt(d)) / (2.0f * a + 1e-5f));
	return -(-b + sqrt(d)) / (2.0f * a + 1e-5f);
}


float4 Uberblend(float4 col0, float4 col1)
{
	return float4(
		lerp(
    	lerp((col0.rgb * col0.a + col1.rgb * col1.a) / (col0.a + col1.a + 1e-4f), (col1.rgb), col1.a),
    	lerp((col0.rgb * (1.0 - col1.a) + col1.rgb * col1.a), (col1.rgb), col1.a),
		col0.a),
    min(1.0, 1.0f - (1.0f - col0.a) * (1.0f - col1.a)));
}


float4 GetDecayedColor(float3 world_pos, float3 offset_dir, float offset_len, float decay_time)
{
	float time_mult = 1.0f / (1.0f + max(0.0f, decay_time * 0.8f - 5.0f));
	float4 noise_sample = SAMPLE_TEX2DLOD(muddle_sampler, SamplerLinearWrapClampWrap, float4(frac((world_pos.xy) * float2(0.5f, 1.0f) * 0.002f + float2(time * 0.1f, 0.0f)), 0.0f, 0.0f));	
	float wiggle_scale = 0.4f * pow(saturate((decay_time - 2.5f) * 0.1f), 2.0f);
	offset_dir = (offset_dir + float3((noise_sample.rg - 0.5f) * 2.0f *wiggle_scale, 0.0f));

	float2 screen_coord = Project(world_pos, viewproj_matrix ).xy;
	float2 blur_screen_dir = Project(world_pos + offset_dir, viewproj_matrix ).xy - screen_coord;

	float3 decayed_coord = world_pos;
	decayed_coord += offset_dir * (1.0f / (1.0f + offset_len / 50.0f)) * 50.0f;
	float2 decayed_screen_coord = Project(decayed_coord, viewproj_matrix ).xy;
	float2 blurred_screen_coord = decayed_screen_coord + blur_screen_dir * (SmoothStep(rand3(int3((decayed_coord).xyz * 0.6f)), 0.3f, -0.6f) - 0.3f) * 200.0f;
	float3 blurred_reprojected_coord = Unproject(blurred_screen_coord, SAMPLE_TEX2DLOD(depth_sampler, SamplerLinearClamp, float4(blurred_screen_coord * src_frame_to_dynamic_scale.xy, 0.0f, 0.0f)).r, inv_viewproj_matrix);


	
	float freq = 0.0003f;
	float grayscale = pow(SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4((blurred_reprojected_coord.xy * freq), 0.0f, 0.0f)).b, 1.0f) * 0.95f;

	float4 noise_sample2 = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(((blurred_reprojected_coord.xy) * 0.0001f + float2(0.0f, time * 0.008f)), 0.0f, 0.0f)) * 0.95f;
	grayscale *= (1.3f + noise_sample2.b * 0.7) / 1.8f;
	
	float temperature = lerp(1800.0f, 2800.0f, time_mult) * pow(saturate(grayscale), 3.0f);// * saturate(1.0f - global_stability);
	
	return float4(BlackBody(temperature).bgr, 1.0f);
}


float4 GetSpaceDecayedColor(float3 world_pos, float3 offset_dir, float offset_len, float decay_time)
{
	float time_mult = 1.0f / (1.0f + max(0.0f, decay_time * 0.8f - 5.0f));
	float4 noise_sample = SAMPLE_TEX2DLOD(muddle_sampler, SamplerLinearWrapClampWrap, float4(frac((world_pos.xy) * float2(0.5f, 1.0f) * 0.002f + float2(time * 0.1f, 0.0f)), 0.0f, 0.0f));	
	float wiggle_scale = 0.4f * pow(saturate((decay_time - 2.5f) * 0.1f), 2.0f);
	offset_dir = (offset_dir + float3((noise_sample.rg - 0.5f) * 2.0f *wiggle_scale, 0.0f));

	float2 screen_coord = Project(world_pos, viewproj_matrix ).xy;
	float2 blur_screen_dir = Project(world_pos + offset_dir * 0.5f, viewproj_matrix ).xy - screen_coord;

	float3 decayed_coord = world_pos;
	decayed_coord += offset_dir * (1.0f / (1.0f + offset_len / 50.0f)) * 50.0f;
	float2 decayed_screen_coord = Project(decayed_coord, viewproj_matrix ).xy;
	float2 blurred_screen_coord = decayed_screen_coord + blur_screen_dir * (SmoothStep(rand3(int3((decayed_coord).xyz * 0.6f)), 0.3f, -0.6f) - 0.3f) * 200.0f;
	float3 blurred_reprojected_coord = Unproject(blurred_screen_coord, SAMPLE_TEX2DLOD(depth_sampler, SamplerLinearClamp, float4(blurred_screen_coord * src_frame_to_dynamic_scale.xy, 0.0f, 0.0f)).r, inv_viewproj_matrix);


	
	float freq = 0.0003f;
	float grayscale = pow(SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4((blurred_reprojected_coord.xy * freq), 0.0f, 0.0f)).b, 1.0f) * 0.95f;

	float4 noise_sample2 = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(((blurred_reprojected_coord.xy) * 0.0001f + float2(0.0f, time * 0.008f)), 0.0f, 0.0f)) * 0.95f;
	grayscale *= (1.3f + noise_sample2.b * 0.7) / 1.8f;
	
	float temperature = lerp(1800.0f, 2800.0f, time_mult) * pow(saturate(grayscale), 3.0f);// * saturate(1.0f - global_stability);
	
	//float4 space_color = SAMPLE_TEX2DLOD(space_tex_sampler, SamplerLinearWrap, float4(screen_coord * 1.7f, 0.0f, 0.0f));
	float4 space_color = SAMPLE_TEX2DLOD(space_tex_sampler, SamplerLinearWrap, float4(blurred_reprojected_coord.xy * 1e-3f, 0.0f, 0.0f));
	float transform_ratio = /*saturate(1.0f - time_mult) * */pow(saturate(grayscale), 1.0f);
	return space_color;//space_color * (transform_ratio > 0.8f ? 1.0f : 0.0f);//lerp(space_color, 0.0f, 1.0f / (1.0f + 1e-3f * temperature));
}

float3 Color(int r, int g, int b)
{
	return pow(float3(r, g, b) / 255.0f, 2.2f);
}
float4 GetSynthesisColor(float3 world_pos, float3 world_normal)
{
	float2 base_screen_coord = Project(world_pos, viewproj_matrix ).xy;
	
	DecayField decay_field = GetDecayField(world_pos);

	float stability_ratio = decay_field.stability;

	float3 offset_dir = -decay_field.gradient / length(decay_field.gradient + 1e-5f);
	float offset_len = GetDecayOffsetLen(decay_field);
		
	float decay_time = decay_field.decay_time;
	//decay_time = lerp(decay_time, 0.0f, saturate(stability_ratio));
	

	if(stability_ratio > 0.0f)
	{
		offset_len = lerp(offset_len, 0.0f, 1.0f - pow(saturate(1.0f - stability_ratio - 0.7f), 5.0f));
	}
	
	float3 offset_world_pos = world_pos - offset_dir * offset_len;
	float3 screen_point = Project(offset_world_pos, viewproj_matrix );
	
	float4 color = SAMPLE_TEX2DLOD( source_sampler, SamplerLinearClamp, float4(screen_point.xy * src_frame_to_dynamic_scale.xy, 0.0f, 0.0f));
	
	float freq = 0.003f / 2.0f;
	float4 sample_x = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(offset_world_pos.yz * freq, 0.0f, 0.0f));
	float4 sample_y = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(offset_world_pos.xz * freq, 0.0f, 0.0f));
	float4 sample_z = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(offset_world_pos.xy * freq, 0.0f, 0.0f));
	
	float4 triplanar_noise = (sample_x * abs(world_normal.x) + sample_y * abs(world_normal.y) + sample_z * abs(world_normal.z)) / (abs(world_normal.x) + abs(world_normal.y) + abs(world_normal.z));

	float decay_dissolve_ratio = 0.0f;
	float decay_black_ratio = 0.0f;
	float3 decay_glow_color = 0.0f;
	{
		float noise_val = triplanar_noise.b;
		noise_val = noise_val - 1.0f + pow(max(0.0f, decay_time), 0.2f) * 1.05f;
		decay_dissolve_ratio = noise_val;
		decay_glow_color *= ((decay_dissolve_ratio < 1.0f) ? 1.0f : 0.0f);
	}

	float dissolve_ratio = decay_dissolve_ratio;
	dissolve_ratio = lerp(dissolve_ratio, 0.0f, saturate(stability_ratio));
	float black_ratio = pow(saturate(dissolve_ratio), 4.0f);
	
	float3 glow_color = BlackBody(pow(saturate(dissolve_ratio), 7.0f) * 2900.0f * decay_field.temp_mult).bgr * (dissolve_ratio < 1.0f ? 1.0f : 0.0f);
	
	[branch]
	if(dissolve_ratio > 1.0f)
	{
		color.rgb = saturate(GetDecayedColor(world_pos, offset_dir, offset_len, decay_time).rgb);
		color.a = 0.0f;
	}
	else
	{
		color.rgb = lerp(color.rgb, 0.0f * color.rgb, black_ratio);
		color.a = (1.0f - black_ratio);
	}
	color.rgb += glow_color * decay_field.glow_mult;

	return color;
}

float4 GetShaperDecayColor(float3 world_pos, float3 world_normal)
{
	float2 base_screen_coord = Project(world_pos, viewproj_matrix ).xy;
	
	DecayField decay_field = GetDecayField(world_pos);

	float stability_ratio = decay_field.stability;

	float3 offset_dir = -decay_field.gradient / length(decay_field.gradient + 1e-5f);
	float offset_len = GetDecayOffsetLen(decay_field) * 0.0f;
		
	float decay_time = decay_field.decay_time;
	//decay_time = lerp(decay_time, 0.0f, saturate(stability_ratio));
		
	float3 offset_world_pos = world_pos - offset_dir * offset_len;
	float3 screen_point = Project(offset_world_pos, viewproj_matrix );
	
	float4 color = SAMPLE_TEX2DLOD( source_sampler, SamplerLinearClamp, float4(screen_point.xy * src_frame_to_dynamic_scale.xy, 0.0f, 0.0f));
	
	float freq = 0.001f / 2.0f;
	float4 sample_x = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(offset_world_pos.yz * freq, 0.0f, 0.0f));
	float4 sample_y = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(offset_world_pos.xz * freq, 0.0f, 0.0f));
	float4 sample_z = SAMPLE_TEX2DLOD(crack_sdm_sampler, SamplerLinearWrap, float4(offset_world_pos.xy * freq, 0.0f, 0.0f));
	
	float4 triplanar_noise = (sample_x * abs(world_normal.x) + sample_y * abs(world_normal.y) + sample_z * abs(world_normal.z)) / (abs(world_normal.x) + abs(world_normal.y) + abs(world_normal.z));

	float decay_dissolve_ratio = 0.0f;
	float decay_black_ratio = 0.0f;
	float3 decay_glow_color = 0.0f;
	{
		float noise_val = triplanar_noise.b;
		noise_val = noise_val - 1.0f + pow(max(0.0f, decay_time), 0.4f) * 1.05f;
		decay_dissolve_ratio = noise_val;
		decay_glow_color *= ((decay_dissolve_ratio < 1.0f) ? 1.0f : 0.0f);
	}

	float dissolve_ratio = decay_dissolve_ratio;
	float black_ratio = pow(saturate(dissolve_ratio), 4.0f);
	
	[branch]
	if(dissolve_ratio > 1.0f)
	{
		//float2 distortion = (SAMPLE_TEX2DLOD(muddle_sampler, SamplerLinearWrap, float4(screen_uv * 1.0f + time * 1e-1f, 0.0f, 0.0f)).xy - 0.5f) * 1e-2f;
		//color.rgb = SAMPLE_TEX2DLOD(space_tex_sampler, SamplerLinearWrap, float4(screen_uv * 1.61f + distortion, 0.0f, 0.0f)).rgb * 0.0f;
		color.rgb = GetSpaceDecayedColor(world_pos, offset_dir, offset_len, decay_time);
		color.a = 0.0f;
	}
	else
	{
		color.rgb = lerp(color.rgb, 0.0f * color.rgb, black_ratio);
		color.a = (1.0f - black_ratio);
	}

	return color;
}


float4 ApplyBreach(float4 colour, float3 world_pos)
{
	// sphere test
	float3 direction = world_pos.xyz - sphere_info.xyz;
	float _distance = length( direction );
	if ( _distance < sphere_info.w )
	{
		// apply the color shift
		colour.rgb = SAMPLE_TEX3DLOD( breach_transform_sampler, SamplerPointClamp, float4( pow( saturate(colour.rgb), 1.0 / 2.2 ), 0.f ) ).rgb;

		// apply the edge texture
		float edge_thickness = 125.f;
		float inner_radius = sphere_info.w - edge_thickness;
		if ( _distance > inner_radius )
		{
			float2 edge_uv;
			direction = normalize( direction );
			edge_uv.x = abs( dot( direction, float3( 1.f, 0.f, 0.f ) ) ) * 4.f;
			edge_uv.y = ( _distance - inner_radius ) / edge_thickness;

			float2 muddle = edge_uv * muddle_sampler_info.x + breach_time * muddle_sampler_info.yz;
			edge_uv = edge_uv + ( SAMPLE_TEX2D( muddle_sampler, SamplerLinearWrapClampWrap, muddle ).rg - 0.5 ) * muddle_sampler_info.w;
			edge_uv.y = lerp( 0.01f, 0.99f, saturate( edge_uv.y ) );

			float4 edge = SAMPLE_TEX2DLOD( breach_edge_sampler, SamplerLinearWrapClampWrap, float4( edge_uv, 0.f, 0.f ) );
			colour.rgb = lerp( colour.rgb, edge.rgb, edge.a );
		}
	}
	return colour;
}

float4 PostProcessPS( PInput input ) : PIXEL_RETURN_SEMANTIC
{
	float2 screen_coord = (input.screen_coord.xy / float2(target_width, target_height)) / target_frame_to_dynamic_scale.xy;
	float2 dynamic_tex_coord = screen_coord.xy * src_frame_to_dynamic_scale.xy;

	/*{
		float2 pixel_coord = input.screen_coord.xy;
		float2 uv_coord = (pixel_coord - float2(1500.0f, 300.0f)) / float2(500.0f, 500.0f);
		if(uv_coord.x < 0.0f || uv_coord.y < 0.0f || uv_coord.x > 1.0f || uv_coord.y > 1.0f)
			return float4(0.1f, 0.1f, 0.1f, 0.0f);
		
		return GetResourceOrbColor(uv_coord);
	}*/

	float depth = SAMPLE_TEX2DLOD(depth_sampler, SamplerLinearClamp, float4(dynamic_tex_coord, 0.0f, 0.0f)).r;
	
	float3 world_pos = Unproject(screen_coord, depth, inv_viewproj_matrix );
	float3 tmp = normalize(cross(ddx(world_pos), ddy(world_pos)));
	float3 world_normal = tmp + 1e-3f;

	#if DETAIL_LEVEL > 0
	if( shimmer_enable )
	{
		float4 shimmer_amount = SAMPLE_TEX2D( shimmer_sampler, SamplerLinearClamp, dynamic_tex_coord );
		//return float4(( shimmer_amount.xy - shimmer_amount.zw) * 2.0f, 0.0f, 1.0f);
		screen_coord += ( shimmer_amount.xy - shimmer_amount.zw ) * 0.05f;
		dynamic_tex_coord = screen_coord.xy * src_frame_to_dynamic_scale.xy;
		
		world_pos = Unproject(screen_coord, depth, inv_viewproj_matrix );
	}
	#endif
	
	float4 colour = SAMPLE_TEX2DLOD( source_sampler, SamplerLinearClamp, float4(dynamic_tex_coord.xy, 0.0f, 0.0f) );
	float initial_alpha = colour.a;
	
	bool decay_started = (GetGlobalDecayTime() > 0.0f);
	[branch]
	if(decay_enable && decay_started)
	{
		[branch]
		if(decay_map_type < 1.0f)
			colour = GetSynthesisColor(world_pos, world_normal);
		else
			colour = GetShaperDecayColor(world_pos, world_normal);
	}else
	{
		#if DETAIL_LEVEL > 0
		{
			if(length(blur_params.xy) > 1e-3f)
			{
				colour = GetRadialBlur(screen_coord.xy, blur_params.xy, blur_params.z);
			}
		}
		#endif
		colour.rgb += world_normal * 1e-5f;
		colour.a = 1.0f;
	}
	#if DETAIL_LEVEL > 0
	{
		float3 bloom = SAMPLE_TEX2DLOD( bloom_sampler, SamplerLinearClampNoBias, float4(screen_coord.xy, 0.0f, 0.0f )).rgb;
		//colour.rgb = 1.0f - exp(-(colour.rgb * original_intensity + bloom) * 1.0f);
		colour.rgb = (colour.rgb * original_intensity + bloom);
	}
	#endif
	
	if(exposure > 1.0f + 1e-5f)
	{
		colour.rgb = ApplyToneMapping(colour.rgb, exposure);
	}
	
	if( desaturation_enable )
	{
		colour = ApplyDesaturation(colour, dynamic_tex_coord);
	}
	
	if( overlay_intensity > 1e-3f )
	{
		colour = ApplyOverlay(colour, screen_coord);
	}
	

	if( post_transform_enable )
	{
		colour.rgb = lerp(
			SAMPLE_TEX3DLOD( post_transform_sampler0, SamplerLinearClamp, float4( pow( saturate(colour.rgb), 1.0 / 2.2 ), 0.f ) ).rgb,
			SAMPLE_TEX3DLOD( post_transform_sampler1, SamplerLinearClamp, float4( pow( saturate(colour.rgb), 1.0 / 2.2 ), 0.f ) ).rgb,
			post_transform_ratio);
	}
	
	#if DETAIL_LEVEL > 0
	{
		colour += rand(input.screen_coord.xy) * 1e-3f;
		colour = ApplyVignette(colour, screen_coord);
	}
	#endif

	if( fade_enable )
	{
		colour *= fade_amount;
		//colour = float4(lerp(colour.rgb, fade_color.rgb, fade_amount), colour.a);
	}
	
	if(breach_enable)
	{
		colour = ApplyBreach(colour, world_pos);
	}
	
	colour.a = initial_alpha;
	
	return colour;
}


Includes = {
	"cw/pdxmesh_blendshapes.fxh"
	"cw/pdxmesh.fxh"
	"cw/utility.fxh"
	"cw/shadow.fxh"
	"cw/camera.fxh"
	"cw/alpha_to_coverage.fxh"
	"jomini/jomini_lighting.fxh"
	"jomini/jomini_fog.fxh"
	"jomini/portrait_accessory_variation.fxh"
	"jomini/portrait_decals.fxh"
	"jomini/portrait_user_data.fxh"
	"constants.fxh"
}

PixelShader =
{
	TextureSampler DiffuseMap
	{
		Index = 0
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler PropertiesMap
	{
		Index = 1
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler NormalMap
	{
		Index = 2
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler SSAOColorMap
	{
		Index = 3
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler EnvironmentMap
	{
		Ref = JominiEnvironmentMap
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Clamp"
		SampleModeV = "Clamp"
		Type = "Cube"
	}
	TextureSampler DiffuseMapOverride
	{
		Index = 9
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler NormalMapOverride
	{
		Index = 10
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler PropertiesMapOverride
	{
		Index = 11
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Wrap"
		SampleModeV = "Wrap"
	}
	TextureSampler ShadowTexture
	{
		Ref = PdxShadowmap
		MagFilter = "Linear"
		MinFilter = "Linear"
		MipFilter = "Linear"
		SampleModeU = "Clamp"
		SampleModeV = "Clamp"
		CompareFunction = less_equal
		SamplerType = "Compare"
	}

	VertexStruct PS_COLOR_SSAO
	{
		float4 Color : PDX_COLOR0;
		float4 SSAOColor : PDX_COLOR1;
	};
}

VertexStruct VS_OUTPUT_PDXMESHPORTRAIT
{
    float4 	Position		: PDX_POSITION;
	float3 	Normal			: TEXCOORD0;
	float3 	Tangent			: TEXCOORD1;
	float3 	Bitangent		: TEXCOORD2;
	float2 	UV0				: TEXCOORD3;
	float2 	UV1				: TEXCOORD4;
	float2 	UV2				: TEXCOORD5;
	float3 	WorldSpacePos	: TEXCOORD6;
	# This instance index is used to fetch custom user data from the Data[] array (see pdxmesh.fxh)
	uint 	InstanceIndex	: TEXCOORD7;
};

VertexStruct VS_INPUT_PDXMESHSTANDARD_ID
{
    float3 Position			: POSITION;
	float3 Normal      		: TEXCOORD0;
	float4 Tangent			: TEXCOORD1;
	float2 UV0				: TEXCOORD2;
@ifdef PDX_MESH_UV1     	
	float2 UV1				: TEXCOORD3;
@endif
@ifdef PDX_MESH_UV2
	float2 UV2				: TEXCOORD4;
@endif


	uint2 InstanceIndices 	: TEXCOORD5;
	
@ifdef PDX_MESH_SKINNED
	uint4 BoneIndex 		: TEXCOORD6;
	float3 BoneWeight		: TEXCOORD7;
@endif

	uint VertexID			: PDX_VertexID;
};

# Portrait constants (SPortraitConstants)
VertexStruct LightDirT
{
	float3		vDirection	: COMMENT;
	uint		Type 		: COMMENT;
};

ConstantBuffer( 5 )
{
	float4 		vPaletteColorSkin;
	float4 		vPaletteColorEyes;
	float4 		vPaletteColorHair;
	float4		vSkinPropertyMult;
	float4		vEyesPropertyMult;
	float4		vHairPropertyMult;
	
	float4 		Light_Color_Falloff[3];
	float4 		Light_Position_Radius[3];
	LightDirT	Light_Direction_Type[3];
	float4 		Light_InnerCone_OuterCone_AffectedByShadows[3];
	
	int			DecalCount;
	int         PreSkinColorDecalCount;
	int			TotalDecalCount;
	int 		_; // Alignment

	float4 		PatternColorOverrides[16];

	float		HasDiffuseMapOverride;
	float		HasNormalMapOverride;
	float		HasPropertiesMapOverride;
};
Code
[[
	#define LIGHT_COUNT 3
	#define LIGHT_TYPE_NONE 0
	#define LIGHT_TYPE_DIRECTIONAL 1
	#define LIGHT_TYPE_SPOTLIGHT 2
	#define LIGHT_TYPE_POINTLIGHT 3
]]

VertexShader = {

	Code
	[[
		VS_OUTPUT_PDXMESHPORTRAIT ConvertOutput( VS_OUTPUT_PDXMESH In )
		{
			VS_OUTPUT_PDXMESHPORTRAIT Out;
			
			Out.Position = In.Position;
			Out.Normal = In.Normal;
			Out.Tangent = In.Tangent;
			Out.Bitangent = In.Bitangent;
			Out.UV0 = In.UV0;
			Out.UV1 = In.UV1;
			Out.UV2 = In.UV2;
			Out.WorldSpacePos = In.WorldSpacePos;
			return Out;
		}
	]]
	
	MainCode VS_portrait_blend_shapes
	{
		Input = "VS_INPUT_PDXMESHSTANDARD_ID"
		Output = "VS_OUTPUT_PDXMESHPORTRAIT"
		Code
		[[
			PDX_MAIN
			{
			  	VS_OUTPUT_PDXMESHPORTRAIT Out;
				
				float4 vPosition = float4( Input.Position.xyz, 1.0f );
				float3 vBlendPositionDiff;
				float3 vBlendNormalDiff;
				float3 vBlendTangentDiff;
				ProcessBlendShapes( vBlendPositionDiff, vBlendNormalDiff, vBlendTangentDiff, Input.VertexID );
				vPosition.xyz += vBlendPositionDiff;
				
				float4x4 WorldMatrix = PdxMeshGetWorldMatrix( Input.InstanceIndices.y );
			#ifdef PDX_MESH_SKINNED
				float4 vSkinnedPosition = float4( 0, 0, 0, 0 );
				float3 vSkinnedNormal = float3( 0, 0, 0 );
				float3 vSkinnedTangent = float3( 0, 0, 0 );
				float3 vSkinnedBitangent = float3( 0, 0, 0 );
			
				float4 vWeight = float4( Input.BoneWeight.xyz, 1.0f - Input.BoneWeight.x - Input.BoneWeight.y - Input.BoneWeight.z );
			
				for( int i = 0; i < PDXMESH_MAX_INFLUENCE; ++i )
			    {
					int nIndex = int( Input.BoneIndex[i] );
					float4x4 mat = BoneMatrices[nIndex + Input.InstanceIndices.x];
					vSkinnedPosition += mul( mat, vPosition ) * vWeight[i];

					float3x3 NormalTransform = CastTo3x3( BoneNormalMatrices[ nIndex + Input.InstanceIndices.x ] );
			
					float3 vNormal = mul( NormalTransform, Input.Normal + vBlendNormalDiff );
					float3 vTangent = mul( NormalTransform, Input.Tangent.xyz + vBlendTangentDiff );
					float3 vBitangent = cross( vNormal, vTangent ) * Input.Tangent.w;
			
					vSkinnedNormal += vNormal * vWeight[i];
					vSkinnedTangent += vTangent * vWeight[i];
					vSkinnedBitangent += vBitangent * vWeight[i];
				}
			
				Out.Position = mul( WorldMatrix, vSkinnedPosition );
				
				Out.Normal = normalize( mul( CastTo3x3(WorldMatrix), normalize( vSkinnedNormal ) ) );
				Out.Tangent = normalize( mul( CastTo3x3(WorldMatrix), normalize( vSkinnedTangent ) ) );
				Out.Bitangent = normalize( mul( CastTo3x3(WorldMatrix), normalize( vSkinnedBitangent ) ) );
			#else
				Out.Position = mul( WorldMatrix, vPosition );
				
				Out.Normal = normalize( mul( CastTo3x3( WorldMatrix ), Input.Normal + vBlendNormalDiff ) );
				Out.Tangent = normalize( mul( CastTo3x3( WorldMatrix ), Input.Tangent.xyz + vBlendTangentDiff ) );
				Out.Bitangent = normalize( cross( Out.Normal, Out.Tangent ) * Input.Tangent.w);
			#endif
			
				Out.WorldSpacePos.xyz = Out.Position.xyz;
				Out.WorldSpacePos /= WorldMatrix[3][3];
				Out.Position = FixProjectionAndMul( ViewProjectionMatrix, Out.Position );
				
				Out.UV0 = Input.UV0;
			#ifdef PDX_MESH_UV1
				Out.UV1 = Input.UV1;
			#else
				Out.UV1 = vec2( 0.0 );
			#endif
			#ifdef PDX_MESH_UV2
				Out.UV2 = Input.UV2;
			#else
				Out.UV2 = vec2( 0.0 );
			#endif
				Out.InstanceIndex = Input.InstanceIndices.y;
				return Out;
			}
		]]
	}

	MainCode VS_portrait_blend_shapes_shadow
	{
		Input = "VS_INPUT_PDXMESHSTANDARD_ID"
		Output = "VS_OUTPUT_PDXMESHSHADOWSTANDARD"
		Code
		[[
			PDX_MAIN
			{
			  	VS_OUTPUT_PDXMESHSHADOWSTANDARD Out;
				
				float4 vPosition = float4( Input.Position.xyz, 1.0 );
				float3 vBlendPositionDiff;
				ProcessBlendShapesPositionOnly( vBlendPositionDiff, Input.VertexID );
				vPosition.xyz += vBlendPositionDiff;
				
				float4x4 WorldMatrix = PdxMeshGetWorldMatrix( Input.InstanceIndices.y );
			#ifdef PDX_MESH_SKINNED
				float4 vSkinnedPosition = float4( 0, 0, 0, 0 );
			
				float4 vWeight = float4( Input.BoneWeight.xyz, 1.0f - Input.BoneWeight.x - Input.BoneWeight.y - Input.BoneWeight.z );
				for( int i = 0; i < PDXMESH_MAX_INFLUENCE; ++i )
			    {
					int nIndex = int( Input.BoneIndex[i] );
					float4x4 mat = BoneMatrices[nIndex + Input.InstanceIndices.x];
					vSkinnedPosition += mul( mat, vPosition ) * vWeight[i];
				}
				Out.Position = mul( WorldMatrix, vSkinnedPosition );
			#else
				Out.Position = mul( WorldMatrix, vPosition );
			#endif
			
				Out.Position = FixProjectionAndMul( ViewProjectionMatrix, Out.Position );
				Out.UV_InstanceIndex = float3( Input.UV0, Input.InstanceIndices.y );
				return Out;
			}
		]]
	}
	
	MainCode VS_standard
	{
		Input = "VS_INPUT_PDXMESHSTANDARD"
		Output = "VS_OUTPUT_PDXMESHPORTRAIT"
		Code
		[[
			PDX_MAIN
			{
				VS_OUTPUT_PDXMESHPORTRAIT Out = ConvertOutput( PdxMeshVertexShaderStandard( Input ) );
				Out.InstanceIndex = Input.InstanceIndices.y;
				return Out;
			}
		]]
	}
}

PixelShader =
{
	Code
	[[
		struct SPortraitPointLight
		{
			float3 _Position;
			float _Radius;
			float3 _Color;
			float _Falloff;
		};
		struct SPortraitSpotLight
		{
			SPortraitPointLight	_PointLight;
			float3 _ConeDirection;
			float _ConeInnerCosAngle;
			float _ConeOuterCosAngle;
		};

		SPortraitPointLight GetPortraitPointLight( float4 PositionAndRadius, float4 ColorAndFalloff )
		{
			SPortraitPointLight PointLight;
			PointLight._Position = PositionAndRadius.xyz;
			PointLight._Radius = PositionAndRadius.w;
			PointLight._Color = ColorAndFalloff.xyz;
			PointLight._Falloff = ColorAndFalloff.w;
			return PointLight;
		}
	
		SPortraitSpotLight GetPortraitSpotLight( float4 PositionAndRadius, float4 ColorAndFalloff, float3 Direction, float InnerCosAngle, float OuterCosAngle )
		{
			SPortraitSpotLight Ret;
			Ret._PointLight = GetPortraitPointLight( PositionAndRadius, ColorAndFalloff );
			Ret._ConeDirection = Direction;
			Ret._ConeInnerCosAngle = InnerCosAngle;
			Ret._ConeOuterCosAngle = OuterCosAngle;
			return Ret;
		}
		
		void GGXPointLight( SPortraitPointLight Pointlight, float3 WorldSpacePos, float ShadowTerm, SMaterialProperties MaterialProps, inout float3 DiffuseLightOut, inout float3 SpecularLightOut )
		{
			float3 PosToLight = Pointlight._Position - WorldSpacePos;
			float DistanceToLight = length( PosToLight );

			float LightIntensity = CalcLightFalloff( Pointlight._Radius, DistanceToLight, Pointlight._Falloff );
			if ( LightIntensity > 0.0 )
			{
				SLightingProperties LightingProps;
				LightingProps._ToCameraDir = normalize( CameraPosition - WorldSpacePos );
				LightingProps._ToLightDir = PosToLight / DistanceToLight;
				LightingProps._LightIntensity = Pointlight._Color * LightIntensity;
				LightingProps._ShadowTerm = ShadowTerm;
				LightingProps._CubemapIntensity = 0.0;
				LightingProps._CubemapYRotation = Float4x4Identity();
				
				float3 DiffuseLight;
				float3 SpecularLight;
				CalculateLightingFromLight( MaterialProps, LightingProps, DiffuseLight, SpecularLight );
				DiffuseLightOut += DiffuseLight;
				SpecularLightOut += SpecularLight;
			}
		}
		
		void GGXSpotLight( SPortraitSpotLight Spot, float3 WorldSpacePos, float ShadowTerm, SMaterialProperties MaterialProps, inout float3 DiffuseLightOut, inout float3 SpecularLightOut )
		{
			float3 	PosToLight = Spot._PointLight._Position - WorldSpacePos;
			float 	DistanceToLight = length(PosToLight);
			float3	ToLightDir = PosToLight / DistanceToLight;
			
			float LightIntensity = CalcLightFalloff( Spot._PointLight._Radius, DistanceToLight, Spot._PointLight._Falloff );
			float PdotL = dot( -ToLightDir, Spot._ConeDirection );
			LightIntensity *= smoothstep( Spot._ConeOuterCosAngle, Spot._ConeInnerCosAngle, PdotL );
			if ( LightIntensity > 0.0 )
			{
				SLightingProperties LightingProps;
				LightingProps._ToCameraDir = normalize( CameraPosition - WorldSpacePos );
				LightingProps._ToLightDir = ToLightDir;
				LightingProps._LightIntensity = Spot._PointLight._Color * LightIntensity;
				LightingProps._ShadowTerm = ShadowTerm;
				LightingProps._CubemapIntensity = 0.0;
				LightingProps._CubemapYRotation = Float4x4Identity();
				
				float3 DiffuseLight;
				float3 SpecularLight;
				CalculateLightingFromLight( MaterialProps, LightingProps, DiffuseLight, SpecularLight );
				DiffuseLightOut += DiffuseLight;
				SpecularLightOut += SpecularLight;
			}
		}

		void CalculatePortraitLights( float3 WorldSpacePos, float ShadowTerm, SMaterialProperties MaterialProps, inout float3 DiffuseLightOut, inout float3 SpecularLightOut )
		{
			for( int i = 0; i < LIGHT_COUNT; ++i )
			{
				float3 DiffuseLight = vec3(0);
				float3 SpecularLight = vec3(0);
				
				//Scale color by ShadowTerm
				float4 Color_Fallof = Light_Color_Falloff[i];
				float LightShadowTerm = Light_InnerCone_OuterCone_AffectedByShadows[i].z > 0.5 ? ShadowTerm : 1.0;
				
				if( Light_Direction_Type[i].Type == LIGHT_TYPE_SPOTLIGHT )
				{
					float InnerAngle = Light_InnerCone_OuterCone_AffectedByShadows[i].x;
					float OuterAngle = Light_InnerCone_OuterCone_AffectedByShadows[i].y;
					SPortraitSpotLight Spot = GetPortraitSpotLight( Light_Position_Radius[i], Color_Fallof, Light_Direction_Type[i].vDirection, InnerAngle, OuterAngle );
					GGXSpotLight( Spot, WorldSpacePos, LightShadowTerm, MaterialProps, DiffuseLight, SpecularLight );
				}
				else if( Light_Direction_Type[i].Type == LIGHT_TYPE_POINTLIGHT )
				{
					SPortraitPointLight Light = GetPortraitPointLight( Light_Position_Radius[i], Color_Fallof );
					GGXPointLight( Light, WorldSpacePos, LightShadowTerm, MaterialProps, DiffuseLight, SpecularLight );
				}
				else if( Light_Direction_Type[i].Type == LIGHT_TYPE_DIRECTIONAL )
				{
					SLightingProperties LightingProps;
					LightingProps._ToCameraDir = normalize( CameraPosition - WorldSpacePos );
					LightingProps._ToLightDir = -Light_Direction_Type[i].vDirection;
					LightingProps._LightIntensity = Color_Fallof.rgb;
					LightingProps._ShadowTerm = LightShadowTerm;
					LightingProps._CubemapIntensity = 0.0;
					LightingProps._CubemapYRotation = Float4x4Identity();

					CalculateLightingFromLight( MaterialProps, LightingProps, DiffuseLight, SpecularLight );
				}
				
				DiffuseLightOut += DiffuseLight;
				SpecularLightOut += SpecularLight;
			}
		}

		void DebugReturn( inout float3 Out, SMaterialProperties MaterialProps, SLightingProperties LightingProps, PdxTextureSamplerCube EnvironmentMap, float3 SssColor, float SssMask )
		{
			#if defined(PDX_DEBUG_PORTRAIT_SSS_MASK)
			Out = SssMask;
			#elif defined(PDX_DEBUG_PORTRAIT_SSS_COLOR)
			Out = SssColor;
			#else
			DebugReturn( Out, MaterialProps, LightingProps, EnvironmentMap );
			#endif
		}

		float3 CommonPixelShader( float4 Diffuse, float4 Properties, float3 NormalSample, in VS_OUTPUT_PDXMESHPORTRAIT Input )
		{
			float3x3 TBN = Create3x3( normalize( Input.Tangent ), normalize( Input.Bitangent ), normalize( Input.Normal ) );
			float3 Normal = normalize( mul( NormalSample, TBN ) );
			
			SMaterialProperties MaterialProps = GetMaterialProperties( Diffuse.rgb, Normal, saturate( Properties.a ), Properties.g, Properties.b );
			SLightingProperties LightingProps = GetSunLightingProperties( Input.WorldSpacePos, ShadowTexture );
			
			float3 DiffuseIBL;
			float3 SpecularIBL;
			CalculateLightingFromIBL( MaterialProps, LightingProps, EnvironmentMap, DiffuseIBL, SpecularIBL );
			
			float3 DiffuseLight = vec3(0.0);
			float3 SpecularLight = vec3(0.0);
			CalculatePortraitLights( Input.WorldSpacePos, LightingProps._ShadowTerm, MaterialProps, DiffuseLight, SpecularLight );
			
			float3 Color = DiffuseIBL + SpecularIBL + DiffuseLight + SpecularLight;
			
			float3 SssColor = vec3(0.0f);
			float SssMask = Properties.r;
			#ifdef FAKE_SSS_EMISSIVE
				float3 SkinColor = RGBtoHSV( Diffuse.rgb );
				SkinColor.z = 1.0f;
				SssColor = HSVtoRGB(SkinColor) * SssMask * 0.5f * MaterialProps._DiffuseColor;
				Color += SssColor;
			#endif
			
			Color = ApplyDistanceFog( Color, Input.WorldSpacePos );
			
			DebugReturn( Color, MaterialProps, LightingProps, EnvironmentMap, SssColor, SssMask );			
			return Color;
		}

		// Remaps Value to [IntervalStart, IntervalEnd]
		// Assumes Value is in [0,1] and that 0 <= IntervalStart < IntervalEnd <= 1
		float RemapToInterval( float Value, float IntervalStart, float IntervalEnd )
		{
			return IntervalStart + Value * ( IntervalEnd - IntervalStart );
		}

		// The skin, eye and hair assets come with a special texture  (the "Color Mask", typically packed into 
		// another texture) that determines the Diffuse-PaletteColor blend. Artists also supply a remap interval 
		// used to bias this texture's values; essentially allowing the texture's full range of values to be 
		// mapped into a small interval of the diffuse lerp (e.g. [0.8, 1]).
		// If the texture value is 0.0, that is a special case indicating there shouldn't be any palette color, 
		// (it is used for non-hair things such as hair bands, earrings etc)
		float3 GetColorMaskColorBLend( float3 DiffuseColor, float3 PaletteColor, uint InstanceIndex, float ColorMaskStrength )
		{
			if ( ColorMaskStrength == 0.0 )
			{
				return DiffuseColor;
			}
			else
			{
				float2 Interval = GetColorMaskRemapInterval( InstanceIndex );
				float LerpTarget = RemapToInterval( ColorMaskStrength, Interval.x, Interval.y );
				return lerp( DiffuseColor.rgb, DiffuseColor.rgb * PaletteColor, LerpTarget );
			}
		}
	]]

	MainCode PS_skin
	{
		Input = "VS_OUTPUT_PDXMESHPORTRAIT"
		Output = "PS_COLOR_SSAO"
		Code
		[[
			PDX_MAIN
			{			
				PS_COLOR_SSAO Out;

				float2 UV0 = Input.UV0;
				float4 Diffuse;
				float4 Properties;
				float3 NormalSample;
				

			#ifdef ENABLE_TEXTURE_OVERRIDE
				if ( HasDiffuseMapOverride > 0.5f )
				{
					Diffuse = PdxTex2D( DiffuseMapOverride, UV0 );
				}
				else
				{
					Diffuse = PdxTex2D( DiffuseMap, UV0 );
				}
				if ( HasPropertiesMapOverride > 0.5f )
				{
					Properties = PdxTex2D( PropertiesMapOverride, UV0 );
				}
				else
				{
					Properties = PdxTex2D( PropertiesMap, UV0 );
				}
				if ( HasNormalMapOverride > 0.5f )
				{
					NormalSample = UnpackRRxGNormal( PdxTex2D( NormalMapOverride, UV0 ) );
				}
				else
				{
					NormalSample = UnpackRRxGNormal( PdxTex2D( NormalMap, UV0 ) );
				}
			#else
				Diffuse = PdxTex2D( DiffuseMap, UV0 );
				Properties = PdxTex2D( PropertiesMap, UV0 );
				NormalSample = UnpackRRxGNormal( PdxTex2D( NormalMap, UV0 ) );
			#endif
				
				AddDecals( Diffuse.rgb, NormalSample, Properties, UV0, Input.InstanceIndex, 0, PreSkinColorDecalCount );
				
				float ColorMaskStrength = Diffuse.a;
				Diffuse.rgb = GetColorMaskColorBLend( Diffuse.rgb, vPaletteColorSkin.rgb, Input.InstanceIndex, ColorMaskStrength );
				
				AddDecals( Diffuse.rgb, NormalSample, Properties, UV0, Input.InstanceIndex, PreSkinColorDecalCount, DecalCount );
				
				float3 Color = CommonPixelShader( Diffuse, Properties, NormalSample, Input );
				Out.Color = float4( Color, 1.0f );

				Out.SSAOColor = PdxTex2D( SSAOColorMap, UV0 );
				Out.SSAOColor.rgb *= vPaletteColorSkin.rgb;

				return Out;
			}
			
		]]
	}
	
	MainCode PS_eye
	{
		Input = "VS_OUTPUT_PDXMESHPORTRAIT"
		Output = "PS_COLOR_SSAO"
		Code
		[[
			PDX_MAIN
			{
				PS_COLOR_SSAO Out;

				float2 UV0 = Input.UV0;
				float4 Diffuse = PdxTex2D( DiffuseMap, UV0 );								
				float4 Properties = PdxTex2D( PropertiesMap, UV0 );
				float3 NormalSample = UnpackRRxGNormal( PdxTex2D( NormalMap, UV0 ) );
				
				float ColorMaskStrength = Diffuse.a;
				Diffuse.rgb = GetColorMaskColorBLend( Diffuse.rgb, vPaletteColorEyes.rgb, Input.InstanceIndex, ColorMaskStrength );
				
				float3 Color = CommonPixelShader( Diffuse, Properties, NormalSample, Input );
				Out.Color = float4( Color, 1.0f );
				
				Out.SSAOColor = PdxTex2D( SSAOColorMap, UV0 );
				Out.SSAOColor.rgb *= vPaletteColorEyes.rgb;
	
				return Out;
			}
		]]
	}

	MainCode PS_attachment
	{		
		Input = "VS_OUTPUT_PDXMESHPORTRAIT"
		Output = "PS_COLOR_SSAO"
		Code
		[[
			PDX_MAIN
			{
				PS_COLOR_SSAO Out;

				float2 UV0 = Input.UV0;
				float4 Diffuse = PdxTex2D( DiffuseMap, UV0 );								
				//이부분을 날려버림으로써 잡다한 효과는 없앨 수 있도록
				//float4 Properties = PdxTex2D( PropertiesMap, UV0 );
				//float3 NormalSample = UnpackRRxGNormal( PdxTex2D( NormalMap, UV0 ) );		
				//Properties.r = 1.0; // wipe this clean now, ready to be modified later

				//#ifdef VARIATIONS_ENABLED
				//	ApplyVariationPatterns( Input, Diffuse, Properties, NormalSample );
				//#endif
				
				//아래는 원래 있던 코드. 위에서 날려버린부분을 계산하지 않도록 Diffuse(실제 텍스쳐)부분만 남겨진 상태
				//float3 Color = CommonPixelShader( Diffuse, Properties, NormalSample, Input );
				//이 밑은 아니메 포트레잇 모드에서 사용한 코드인데, 왜 diffuse값을 토막내고 잘라냈는지는 모르겠음. 이러면 색상 데이터가 칼질당할텐데?
				//float3 Color = Diffuse * 0.3f - 0.015f;
				float3 Color = Diffuse;
				Out.Color = float4( Color, Diffuse.a );
				Out.SSAOColor = float4( vec3( 0.0f ), 1.0f );

				return Out;
			}
		]]
	}
	MainCode PS_portrait_hair_backface
	{
		Input = "VS_OUTPUT_PDXMESHPORTRAIT"
		Output = "PDX_COLOR"
		Code
		[[
			PDX_MAIN
			{			
				return float4( vec3( 0.0f ), 1.0f );
			}
		]]
	}
	MainCode PS_hair
	{
		Input = "VS_OUTPUT_PDXMESHPORTRAIT"
		Output = "PS_COLOR_SSAO"
		Code
		[[
			PDX_MAIN
			{
				PS_COLOR_SSAO Out;

				float2 UV0 = Input.UV0;
				float4 Diffuse = PdxTex2D( DiffuseMap, UV0 );								
				float4 Properties = PdxTex2D( PropertiesMap, UV0 );
				Properties *= vHairPropertyMult;
				float4 NormalSampleRaw = PdxTex2D( NormalMap, UV0 );
				float3 NormalSample = UnpackRRxGNormal( NormalSampleRaw ) * ( PDX_IsFrontFace ? 1 : -1 );

				float ColorMaskStrength = NormalSampleRaw.b;
				Diffuse.rgb = GetColorMaskColorBLend( Diffuse.rgb, vPaletteColorHair.rgb, Input.InstanceIndex, ColorMaskStrength );
				
				float3 Color = CommonPixelShader( Diffuse, Properties, NormalSample, Input );

				#ifdef ALPHA_TO_COVERAGE
					Diffuse.a = RescaleAlphaByMipLevel( Diffuse.a, UV0, DiffuseMap );

					const float CUTOFF = 0.5f;
					Diffuse.a = SharpenAlpha( Diffuse.a, CUTOFF );
				#endif

				#ifdef WRITE_ALPHA_ONE
					Out.Color = float4( Color, 1.0f );
				#else
					#ifdef HAIR_TRANSPARENCY_HACK
						// TODO [HL]: Hack to stop clothing fragments from being discarded by transparent hair,
						// proper fix is to ensure that hair is drawn after clothes
						// https://beta.paradoxplaza.com/browse/PSGE-3103
						clip( Diffuse.a - 0.5f );
					#endif

					Out.Color = float4( Color, Diffuse.a );
				#endif

				Out.SSAOColor = PdxTex2D( SSAOColorMap, UV0 );
				Out.SSAOColor.rgb *= vPaletteColorHair.rgb;

				return Out;
			}
		]]
	}
	MainCode PS_hair_double_sided
	{
		Input = "VS_OUTPUT_PDXMESHPORTRAIT"
		Output = "PS_COLOR_SSAO"
		Code
		[[
			PDX_MAIN
			{
				PS_COLOR_SSAO Out;

				float2 UV0 = Input.UV0;
				float4 Diffuse = PdxTex2D( DiffuseMap, UV0 );
				#ifdef ALPHA_TEST
				clip( Diffuse.a - 0.5f );
				Diffuse.a = 1.0f;
				#endif
				float4 Properties = PdxTex2D( PropertiesMap, UV0 );
				float3 NormalSample = UnpackRRxGNormal( PdxTex2D( NormalMap, UV0 ) );

				Properties *= vHairPropertyMult;
				Diffuse.rgb *= vPaletteColorHair.rgb;

				float3 Color = CommonPixelShader( Diffuse, Properties, NormalSample, Input );

				Out.Color = float4( Color, Diffuse.a );
				
				Out.SSAOColor = PdxTex2D( SSAOColorMap, UV0 );
				Out.SSAOColor.rgb *= vPaletteColorHair.rgb;

				return Out;
			}
		]]
	}
}

BlendState hair_alpha_blend
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
	SourceAlpha = "ONE"
	DestAlpha = "INV_SRC_ALPHA"
	WriteMask = "RED|GREEN|BLUE|ALPHA"
}

DepthStencilState hair_alpha_blend
{
	DepthWriteEnable = no
}

BlendState alpha_to_coverage
{
	BlendEnable = no
	WriteMask = "RED|GREEN|BLUE|ALPHA"
	AlphaToCoverage = yes
}

RasterizerState rasterizer_no_culling
{
	CullMode = "none"
}

RasterizerState rasterizer_backfaces
{
	FrontCCW = yes
}
RasterizerState ShadowRasterizerState
{
	#Don't go higher than 10000 as it will make the shadows fall through the mesh
	DepthBias = 500
	SlopeScaleDepthBias = 2
}
RasterizerState ShadowRasterizerStateBackfaces
{
	DepthBias = 1000
	SlopeScaleDepthBias = 2
	FrontCCW = yes
}

Effect portrait_skin
{
	VertexShader = "VS_standard"
	PixelShader = "PS_skin"
	Defines = { "FAKE_SSS_EMISSIVE" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_skinShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_teeth
{
	VertexShader = "VS_standard"
	PixelShader = "PS_skin"
	Defines = { "FAKE_SSS_EMISSIVE" }
}

Effect portrait_teeth
{
	VertexShader = "VS_portrait_blend_shapes"
	PixelShader = "PS_skin"
	Defines = { "FAKE_SSS_EMISSIVE" }
}

Effect portrait_skin_face
{
	VertexShader = "VS_standard"
	PixelShader = "PS_skin"
	Defines = { "FAKE_SSS_EMISSIVE" "ENABLE_TEXTURE_OVERRIDE" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_skin_faceShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDXMESH_DISABLE_DITHERED_OPACITY" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_eye
{
	VertexShader = "VS_standard"
	PixelShader = "PS_eye"
}

Effect portrait_attachment
{
	VertexShader = "VS_standard"
	PixelShader = "PS_attachment"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_attachmentShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDXMESH_DISABLE_DITHERED_OPACITY" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_attachment_pattern
{
	VertexShader = "VS_standard"
	PixelShader = "PS_attachment"
	Defines = { "VARIATIONS_ENABLED" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_attachment_patternShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDXMESH_DISABLE_DITHERED_OPACITY" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_attachment_pattern_alpha_to_coverage
{
	VertexShader = "VS_standard"
	PixelShader = "PS_attachment"
	BlendState = "alpha_to_coverage"
	Defines = { "VARIATIONS_ENABLED" "PDX_MESH_BLENDSHAPES"}
}

Effect portrait_attachment_pattern_alpha_to_coverageShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshAlphaBlendShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDXMESH_DISABLE_DITHERED_OPACITY" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_attachment_variedShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}
####우리가 사용할 쉐이더는 바로 이것! 이게 정확히 뭔지는 잘 모르겠지만, 지금까지의 경험상 투명한 색상을 보존시키려면 alpha머시기라 적힌 것들을 써야할것같다. 아래 PixelShader에 적혀있듯 이건 윗쪽 650번째 줄에 있는 PS_attachment 관련 블록으로 이어지는것같아.
Effect portrait_attachment_alpha_to_coverage
{
	VertexShader = "VS_standard"
	PixelShader = "PS_attachment"
	BlendState = "alpha_to_coverage"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_attachment_alpha_to_coverageShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshAlphaBlendShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_hair
{
	VertexShader = "VS_standard"
	PixelShader = "PS_hair"
	BlendState = "alpha_to_coverage"
	RasterizerState = "rasterizer_no_culling"
	Defines = { "ALPHA_TO_COVERAGE" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_hair_transparency_hack
{
	VertexShader = "VS_standard"
	PixelShader = "PS_hair"
	BlendState = "alpha_to_coverage"
	RasterizerState = "rasterizer_no_culling"
	Defines = { "HAIR_TRANSPARENCY_HACK" "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_hairShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshAlphaBlendShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDXMESH_DISABLE_DITHERED_OPACITY" }
}

Effect portrait_hair_double_sided
{
	VertexShader = "VS_standard"
	PixelShader = "PS_hair_double_sided"
	BlendState = "alpha_to_coverage"
	#DepthStencilState = "test_and_write"
	RasterizerState = "rasterizer_no_culling"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_hair_alpha
{
	VertexShader = "VS_standard"
	PixelShader = "PS_hair"
	BlendState = "hair_alpha_blend"
	DepthStencilState = "hair_alpha_blend"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_hair_opaque
{
	VertexShader = "VS_standard"
	PixelShader = "PS_hair"
	
	Defines = { "WRITE_ALPHA_ONE" "PDX_MESH_BLENDSHAPES" }
}
	
Effect portrait_hair_opaqueShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDXMESH_DISABLE_DITHERED_OPACITY" }
}

Effect portrait_attachment_alpha
{
	VertexShader = "VS_standard"
	PixelShader = "PS_attachment"
	BlendState = "hair_alpha_blend"
	DepthStencilState = "hair_alpha_blend"
}

Effect portrait_attachment_alphaShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshAlphaBlendShadow"
	RasterizerState = "ShadowRasterizerState"
	Defines = { "PDX_MESH_BLENDSHAPES" }
}

Effect portrait_hair_backside
{
	VertexShader = "VS_standard"
	PixelShader = "PS_portrait_hair_backface"
	RasterizerState = "rasterizer_backfaces"
}

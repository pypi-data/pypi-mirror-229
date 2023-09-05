// .NAME vtU3DExporter - create an u3d/idtf/pdf file
// .SECTION Description
// vtkU3DExporter is a render window exporter which writes out the renderered
// scene into an U3D file. U3D is an open format for 3D models that can be embedded
// into PDF files and diplayed by Adobe viewers. IDTF is a text format (similar to VRML)
// for representation 3D scenes that can be converted to U3D.
// .SECTION Thanks
// U3DExporter is contributed by Michail Vidiassov.
#ifndef __vtkU3DExporter_h
#define __vtkU3DExporter_h

#define OBJECT_INTERACTOR_STYLE_EXPORT __declspec( dllexport )

#if defined(_WIN32)
#define VTKU3DEXPORTER_EXPORT __declspec( dllexport )
#else
#define VTKU3DEXPORTER_EXPORT
#endif

#include "vtkIOExportModule.h" // For export macro
#include "vtkExporter.h"

class vtkLight;
class vtkActor;
class vtkActor2D;
class vtkPoints;
class vtkDataArray;
class vtkUnsignedCharArray;
class vtkRenderer;


class VTKU3DEXPORTER_EXPORT vtkU3DExporter : public vtkExporter
{
public:
    static vtkU3DExporter *New();
    vtkTypeMacro(vtkU3DExporter,vtkExporter);

    // Description:
    // Set/Get the output file name.
    vtkSetStringMacro(FileName);
    vtkGetStringMacro(FileName);

    // Description:
    // Set the U3D_LIBDIR env. variable expected by the U3D IFXOSLoader
    // to find and load the IFXCore library.
    //
    // If the U3D_LIBDIR env. variable is already set, this function is a no-op.
    //
    // Notes:
    // * The directory is set based on the location of the vtkU3DExporter python
    //   module.
    //
    // * This function is automatically called from vtkU3DExporter::WriteData()
    void InitializeEnvironment();

    // Description:
    // Specify if compression of meshes is enabled
    vtkSetClampMacro(MeshCompression, int, 0, 1);
    vtkBooleanMacro(MeshCompression, int);
    vtkGetMacro(MeshCompression, int);

    void PrintSelf(ostream & os, vtkIndent indent) override {}
    void PrintHeader(ostream & os, vtkIndent indent) override {}
    void PrintTrailer(ostream & os, vtkIndent indent) override {}

protected:
    vtkU3DExporter();
    ~vtkU3DExporter();

    // Description:
    // Write data to output.
    void WriteData() override;

    char *FileName;
    int MeshCompression;

private:
    vtkU3DExporter(const vtkU3DExporter&);  // Not implemented.
    void operator=(const vtkU3DExporter&);  // Not implemented.

};

#endif

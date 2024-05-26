import src.port.renderer as renderer
import src.port.viewer as viewer
import src.sheet.data as sheet_data


def render_cell(
    session,
    cell_position,
    render_selected=None,
    catch_failure=False,
):
    return renderer.render_cell(
      session,
      cell_position,
      render_selected,
      catch_failure,
    )


def render(session, catch_failure=False):
    upperleft = viewer.get_upperleft(session)
    nrows, ncols = viewer.get_dimensions(session)
    bounds = sheet_data.get_bounds()

    table = renderer.render_table(
        session,
        upperleft=upperleft,
        nrows=nrows,
        ncols=ncols,
        bounds=bounds,
        catch_failure=catch_failure,
    )
    return table

GET_ASSETS = """ 
query (
  $id: ID!,
  $name: String!,
  $page: Int,
  $limit: Int
) {
  assets(
    companyId: $id
    page: $page
    limit: $limit
    search: {
      name: $name
    }
  ) {
    collection {
      id
      name
      createdAt
    }

    metadata {
      currentPage
      limitValue
      totalCount
      totalPages
    }
  }
}
"""

GET_PROJECTS = """
query (
  $project_code: String!,
  $project_label: String!,
  $page: Int,
  $limit: Int
) {
  projects(
    page: $page
    limit: $limit
    params: {
      apiCodeEq: $project_code
      labelEq: $project_label
    }
  ) {
    collection {
      id
      apiCode
      assets {
        id
      }
      company {
        id
        customFeatures
      }
    }
    metadata {
      currentPage
      limitValue
      totalCount
      totalPages
    }
  }
}
"""

GET_COMPANIES = """
query Companies {
  companies (
    limit: 50, 
    order: label,
    orderType: ASC
		
  )  {
    collection {
      id
      label
      customFeatures
    }
  }
}
"""
